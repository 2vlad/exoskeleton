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

from scripts.models import Issue, Document

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
