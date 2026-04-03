"""Raw source data → canonical Pydantic records.

This module handles Tier A (deterministic) extraction from raw API responses.
Each source has its own normalizer that maps source-specific field names
to canonical schema fields.

Rules:
- Never invent data not present in the raw response.
- Skip malformed records instead of crashing.
- Always set provenance fields (source, source_ref, fetched_at, dedupe_key).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from scripts.models import Issue, Document, Note, Relation

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_get(obj: dict, *keys: str, default=None):
    """Safely traverse nested dicts."""
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def normalize_tracker_issue(raw: dict) -> Issue | None:
    """Normalize a single tracker issue response to canonical Issue."""
    key = raw.get("key")
    if not key or not isinstance(key, str):
        logger.warning("Skipping issue with missing/invalid key: %s", raw)
        return None

    summary = raw.get("summary")
    if not summary or not isinstance(summary, str):
        logger.warning("Skipping issue %s with missing summary", key)
        return None

    status = _safe_get(raw, "status", "key") or _safe_get(raw, "status") or "unknown"
    if isinstance(status, dict):
        status = status.get("key", "unknown")

    assignee = _safe_get(raw, "assignee", "id") or _safe_get(raw, "assignee")
    if isinstance(assignee, dict):
        assignee = assignee.get("id")

    reporter = _safe_get(raw, "reporter", "id") or _safe_get(raw, "reporter")
    if isinstance(reporter, dict):
        reporter = reporter.get("id")

    queue = _safe_get(raw, "queue", "key") or _safe_get(raw, "queue")
    if isinstance(queue, dict):
        queue = queue.get("key")

    priority = _safe_get(raw, "priority", "key")
    if isinstance(priority, dict):
        priority = priority.get("key")

    try:
        return Issue(
            id=f"tracker:{key}",
            source="tracker",
            source_type="issue",
            source_ref=key,
            key=key,
            summary=summary,
            status=status,
            assignee=assignee,
            reporter=reporter,
            queue=queue,
            priority=priority,
            updated_at=raw.get("updatedAt"),
            created_at=raw.get("createdAt"),
            entity_refs=[],
            dedupe_key=f"tracker:{key}",
            confidence="canonical",
            fetched_at=_now_iso(),
        )
    except Exception as exc:
        logger.warning("Skipping issue %s due to validation error: %s", key, exc)
        return None


def normalize_tracker_issues(raw_list: list[dict]) -> list[Issue]:
    """Normalize a list of raw tracker issues. Skips malformed ones."""
    results = []
    for raw in raw_list:
        issue = normalize_tracker_issue(raw)
        if issue is not None:
            results.append(issue)
    return results


def normalize_intrasearch_hit(raw: dict, query: str | None = None) -> Document | None:
    """Normalize an intrasearch search result to canonical Document."""
    title = raw.get("title")
    url = raw.get("url")
    if not title or not url:
        logger.warning("Skipping intrasearch hit with missing title/url: %s", raw)
        return None

    return Document(
        id=f"intrasearch:{url}",
        source="intrasearch",
        source_type="document",
        source_ref=url,
        title=title,
        url=url,
        snippet=raw.get("snippet"),
        query=query,
        dedupe_key=f"intrasearch:{url}",
        confidence="canonical",
        fetched_at=_now_iso(),
    )


def normalize_intrasearch_hits(raw_list: list[dict], query: str | None = None) -> list[Document]:
    """Normalize a list of intrasearch hits. Skips malformed ones."""
    results = []
    for raw in raw_list:
        doc = normalize_intrasearch_hit(raw, query=query)
        if doc is not None:
            results.append(doc)
    return results


# --- Tracker comments ---

def normalize_tracker_comment(raw: dict, issue_key: str) -> Note | None:
    """Normalize a single tracker comment to canonical Note."""
    comment_id = raw.get("id")
    text = raw.get("text")
    if not text or not isinstance(text, str):
        logger.warning("Skipping comment with missing text for %s", issue_key)
        return None

    author = _safe_get(raw, "createdBy", "id") or _safe_get(raw, "createdBy")
    if isinstance(author, dict):
        author = author.get("id")

    entity_refs = [f"issue:{issue_key}"]
    if author:
        entity_refs.append(f"person:{author}")

    try:
        return Note(
            id=f"comment:{issue_key}:{comment_id}",
            source="tracker",
            source_type="comment",
            source_ref=f"{issue_key}#comment-{comment_id}",
            kind="note",
            text=text,
            entity_refs=entity_refs,
            dedupe_key=f"comment:{issue_key}:{comment_id}",
            confidence="canonical",
            fetched_at=_now_iso(),
            payload={"createdAt": raw.get("createdAt"), "author": author},
        )
    except Exception as exc:
        logger.warning("Skipping comment %s for %s: %s", comment_id, issue_key, exc)
        return None


def normalize_tracker_comments(raw_list: list[dict], issue_key: str) -> list[Note]:
    """Normalize a list of tracker comments for a given issue."""
    results = []
    for raw in raw_list:
        note = normalize_tracker_comment(raw, issue_key)
        if note is not None:
            results.append(note)
    return results


# --- Tracker links (dependency graph) ---

def normalize_tracker_link(raw: dict, source_key: str) -> Relation | None:
    """Normalize a single tracker issue link to canonical Relation."""
    direction = raw.get("direction")
    link_type_raw = raw.get("type", {})
    link_type = link_type_raw.get("id") if isinstance(link_type_raw, dict) else link_type_raw
    target_key = _safe_get(raw, "issue", "key")

    if not target_key or not link_type:
        logger.warning("Skipping link with missing target/type for %s", source_key)
        return None

    # Map tracker link types to our relation types
    relation_map = {
        "relates": "related_to",
        "depends": "depends_on",
        "blocks": "depends_on",  # reverse direction handled below
        "is subtask for": "belongs_to",
        "parent": "belongs_to",
    }
    relation_type = relation_map.get(link_type, "related_to")

    # For outward links: source → target
    # For inward links: target → source
    if direction == "inward":
        from_ref = f"issue:{target_key}"
        to_ref = f"issue:{source_key}"
    else:
        from_ref = f"issue:{source_key}"
        to_ref = f"issue:{target_key}"

    dedupe = f"link:{source_key}:{direction}:{link_type}:{target_key}"

    try:
        return Relation(
            id=dedupe,
            source="tracker",
            kind="relation",
            from_ref=from_ref,
            to_ref=to_ref,
            relation_type=relation_type,
            dedupe_key=dedupe,
            fetched_at=_now_iso(),
            payload={"direction": direction, "link_type": link_type},
        )
    except Exception as exc:
        logger.warning("Skipping link %s→%s: %s", source_key, target_key, exc)
        return None


def normalize_tracker_links(raw_list: list[dict], source_key: str) -> list[Relation]:
    """Normalize all links for a given issue."""
    results = []
    for raw in raw_list:
        rel = normalize_tracker_link(raw, source_key)
        if rel is not None:
            results.append(rel)
    return results


# --- Tracker goals ---

def normalize_tracker_goal(raw: dict) -> Issue | None:
    """Normalize a tracker goal to canonical Issue (goals are issues with type=goal)."""
    key = raw.get("key")
    summary = raw.get("summary")
    if not key or not summary:
        logger.warning("Skipping goal with missing key/summary: %s", raw)
        return None

    status = _safe_get(raw, "status", "key") or "open"
    if isinstance(status, dict):
        status = status.get("key", "open")

    queue = _safe_get(raw, "queue", "key") or _safe_get(raw, "queue")
    if isinstance(queue, dict):
        queue = queue.get("key")

    parent_key = _safe_get(raw, "parent", "key")
    entity_refs = []
    if parent_key:
        entity_refs.append(f"goal:{parent_key}")

    try:
        return Issue(
            id=f"tracker:{key}",
            source="tracker",
            source_type="goal",
            source_ref=key,
            key=key,
            summary=summary,
            status=status,
            queue=queue,
            entity_refs=entity_refs,
            dedupe_key=f"tracker:{key}",
            confidence="canonical",
            fetched_at=_now_iso(),
            payload={
                "type": "goal",
                "progress": raw.get("progress"),
                "parent": parent_key,
                "children": [c.get("key") for c in raw.get("children", []) if c.get("key")],
            },
        )
    except Exception as exc:
        logger.warning("Skipping goal %s: %s", key, exc)
        return None


def normalize_tracker_goals(raw_list: list[dict]) -> tuple[list[Issue], list[Relation]]:
    """Normalize goals and extract parent→child relations."""
    goals = []
    relations = []
    for raw in raw_list:
        goal = normalize_tracker_goal(raw)
        if goal is None:
            continue
        goals.append(goal)
        # Create parent→child relations
        for child in raw.get("children", []):
            child_key = child.get("key")
            if not child_key:
                continue
            try:
                rel = Relation(
                    id=f"goal_rel:{goal.key}:{child_key}",
                    source="tracker",
                    kind="relation",
                    from_ref=f"issue:{goal.key}",
                    to_ref=f"issue:{child_key}",
                    relation_type="belongs_to",
                    dedupe_key=f"goal_rel:{goal.key}:{child_key}",
                    fetched_at=_now_iso(),
                    payload={"type": "parent_of"},
                )
                relations.append(rel)
            except Exception as exc:
                logger.warning("Skipping goal relation %s→%s: %s", goal.key, child_key, exc)
    return goals, relations


# --- Calendar events ---

def normalize_calendar_event(raw: dict) -> Note | None:
    """Normalize a calendar event to a Note with kind=note."""
    event_id = raw.get("id")
    name = raw.get("name")
    if not name:
        logger.warning("Skipping calendar event with missing name: %s", raw)
        return None

    attendees = raw.get("attendees", [])
    attendee_logins = [a.get("login") for a in attendees if a.get("login")]
    entity_refs = [f"person:{login}" for login in attendee_logins]

    text = f"Meeting: {name}"
    if raw.get("start"):
        text += f" | {raw['start']}"
    if attendee_logins:
        text += f" | with: {', '.join(attendee_logins)}"

    try:
        return Note(
            id=f"cal:{event_id}",
            source="calendar",
            source_type="calendar_event",
            source_ref=event_id,
            kind="note",
            text=text,
            entity_refs=entity_refs,
            dedupe_key=f"cal:{event_id}",
            confidence="canonical",
            fetched_at=_now_iso(),
            payload={
                "event_id": event_id,
                "name": name,
                "start": raw.get("start"),
                "end": raw.get("end"),
                "attendees": attendee_logins,
                "description": raw.get("description"),
            },
        )
    except Exception as exc:
        logger.warning("Skipping calendar event %s: %s", event_id, exc)
        return None


def normalize_calendar_events(raw_list: list[dict]) -> list[Note]:
    """Normalize a list of calendar events."""
    results = []
    for raw in raw_list:
        note = normalize_calendar_event(raw)
        if note is not None:
            results.append(note)
    return results
