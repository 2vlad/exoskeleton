"""Rebuild markdown views from ledger data.

Views are PROJECTIONS of the ledger — never canonical storage.
The model does not maintain these files directly (PRD §12.2.1).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from scripts.merge_ledger import read_jsonl

logger = logging.getLogger(__name__)


def _read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _read_state(brain_dir: Path) -> dict:
    state_path = brain_dir / "state" / "source_state.json"
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {}


def rebuild_active_view(brain_dir: Path) -> str:
    """Rebuild brain/views/active.md from ledger + control files."""
    issues = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
    commitments = read_jsonl(brain_dir / "ledger" / "commitments.jsonl")
    role_text = _read_text(brain_dir / "control" / "role.md")
    week_text = _read_text(brain_dir / "control" / "week.md")
    state = _read_state(brain_dir)

    lines = ["# Active Work", ""]

    if role_text.strip():
        lines.append("## Role")
        for line in role_text.strip().split("\n"):
            if not line.startswith("# "):
                lines.append(line)
        lines.append("")

    if week_text.strip():
        lines.append("## Week Focus")
        for line in week_text.strip().split("\n"):
            if not line.startswith("# "):
                lines.append(line)
        lines.append("")

    active_issues = [i for i in issues if i.get("status") not in ("closed", "resolved", "cancelled")]
    active_issues.sort(key=lambda x: (x.get("queue") or "", x.get("priority") or "zzz"))

    lines.append("## My Issues")
    lines.append("")
    if active_issues:
        lines.append("| Key | Summary | Status | Priority | Queue | Updated |")
        lines.append("|-----|---------|--------|----------|-------|---------|")
        for issue in active_issues:
            lines.append(
                f"| {issue.get('key', '?')} "
                f"| {issue.get('summary', '?')} "
                f"| {issue.get('status', '?')} "
                f"| {issue.get('priority', '-')} "
                f"| {issue.get('queue', '-')} "
                f"| {issue.get('updated_at', '-')[:10] if issue.get('updated_at') else '-'} |"
            )
    else:
        lines.append("_No active issues found._")
    lines.append("")

    active_comms = [c for c in commitments if c.get("status") == "active"]
    if active_comms:
        lines.append("## Active Commitments")
        lines.append("")
        for c in active_comms:
            due = c.get("due_date", "no date")
            lines.append(f"- **{c.get('summary', '?')}** — owner: {c.get('owner', '?')}, due: {due}")
        lines.append("")

    last_sync = state.get("last_sync", {})
    health = state.get("source_health", {})
    if last_sync:
        lines.append("## Sync Freshness")
        lines.append("")
        for source, ts in sorted(last_sync.items()):
            status = health.get(source, "unknown")
            lines.append(f"- **{source}**: last sync {ts[:10] if ts else 'never'} — {status}")
        lines.append("")

    degraded = [s for s, h in health.items() if h != "ok"]
    if degraded:
        lines.append("## Degraded Sources")
        lines.append("")
        for s in degraded:
            lines.append(f"- {s}: {health[s]}")
        lines.append("")

    return "\n".join(lines)


def rebuild_decisions_view(brain_dir: Path) -> str:
    """Rebuild brain/views/decisions.md from ledger."""
    decisions = read_jsonl(brain_dir / "ledger" / "decisions.jsonl")
    decisions.sort(key=lambda x: x.get("decided_at") or x.get("fetched_at", ""), reverse=True)

    lines = ["# Decisions", ""]
    if not decisions:
        lines.append("_No decisions recorded._")
        return "\n".join(lines)

    for d in decisions:
        date = (d.get("decided_at") or d.get("fetched_at", "?"))[:10]
        lines.append(f"### {d.get('summary', '?')}")
        lines.append("")
        if d.get("context"):
            lines.append(f"**Context:** {d['context']}")
        if d.get("decided_by"):
            lines.append(f"**Decided by:** {d['decided_by']}")
        lines.append(f"**Date:** {date}")
        lines.append(f"**Source:** {d.get('source', '?')} ({d.get('source_ref', '?')})")
        if d.get("confidence") != "canonical":
            lines.append(f"**Confidence:** {d.get('confidence')}")
        refs = d.get("entity_refs", [])
        if refs:
            lines.append(f"**Related:** {', '.join(refs)}")
        lines.append("")

    return "\n".join(lines)


def rebuild_commitments_view(brain_dir: Path) -> str:
    """Rebuild brain/views/commitments.md from ledger."""
    commitments = read_jsonl(brain_dir / "ledger" / "commitments.jsonl")

    active = [c for c in commitments if c.get("status") == "active"]
    fulfilled = [c for c in commitments if c.get("status") == "fulfilled"]
    stale = [c for c in commitments if c.get("status") == "stale"]

    lines = ["# Commitments", ""]

    def _render_group(title: str, items: list[dict]):
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        for c in items:
            due = c.get("due_date", "no date")
            owner = c.get("owner", "?")
            lines.append(f"- **{c.get('summary', '?')}** — owner: {owner}, due: {due}")
            lines.append(f"  Source: {c.get('source', '?')} ({c.get('source_ref', '?')})")
        lines.append("")

    _render_group("Active", active)
    _render_group("Stale", stale)
    _render_group("Fulfilled", fulfilled)

    if not commitments:
        lines.append("_No commitments recorded._")

    return "\n".join(lines)


def rebuild_project_view(brain_dir: Path, project_id: str, project_name: str) -> str:
    """Rebuild a single project dossier from ledger data."""
    issues = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
    decisions = read_jsonl(brain_dir / "ledger" / "decisions.jsonl")
    commitments = read_jsonl(brain_dir / "ledger" / "commitments.jsonl")
    docs = read_jsonl(brain_dir / "ledger" / "docs.jsonl")
    relations = read_jsonl(brain_dir / "ledger" / "relations.jsonl")

    ref = f"project:{project_id}"

    proj_issues = [i for i in issues if ref in i.get("entity_refs", [])]
    proj_decisions = [d for d in decisions if ref in d.get("entity_refs", [])]
    proj_commitments = [c for c in commitments if ref in c.get("entity_refs", [])]
    proj_docs = [d for d in docs if ref in d.get("entity_refs", [])]

    related_issue_ids = {
        r["to_ref"] for r in relations
        if r.get("from_ref") == ref and r.get("relation_type") == "belongs_to"
    }
    for issue in issues:
        if issue.get("id") in related_issue_ids and issue not in proj_issues:
            proj_issues.append(issue)

    lines = [f"# {project_name}", ""]
    lines.append(f"_Project ID: {project_id}_")
    lines.append("")

    lines.append("## Issues")
    lines.append("")
    if proj_issues:
        for i in proj_issues:
            lines.append(f"- **{i.get('key')}** {i.get('summary', '?')} — {i.get('status', '?')}")
    else:
        lines.append("_No linked issues._")
    lines.append("")

    lines.append("## Decisions")
    lines.append("")
    if proj_decisions:
        for d in proj_decisions:
            lines.append(f"- {d.get('summary', '?')} ({(d.get('decided_at') or '?')[:10]})")
    else:
        lines.append("_No linked decisions._")
    lines.append("")

    lines.append("## Commitments")
    lines.append("")
    if proj_commitments:
        for c in proj_commitments:
            lines.append(f"- {c.get('summary', '?')} — due: {c.get('due_date', '?')}")
    else:
        lines.append("_No linked commitments._")
    lines.append("")

    lines.append("## Related Documents")
    lines.append("")
    if proj_docs:
        for d in proj_docs:
            lines.append(f"- [{d.get('title', '?')}]({d.get('url', '#')})")
    else:
        lines.append("_No linked documents._")
    lines.append("")

    return "\n".join(lines)


def rebuild_all_views(brain_dir: Path) -> dict:
    """Rebuild all standard views. Returns stats."""
    views_dir = brain_dir / "views"
    views_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    active_md = rebuild_active_view(brain_dir)
    (views_dir / "active.md").write_text(active_md, encoding="utf-8")
    results["active"] = len(active_md)

    decisions_md = rebuild_decisions_view(brain_dir)
    (views_dir / "decisions.md").write_text(decisions_md, encoding="utf-8")
    results["decisions"] = len(decisions_md)

    commitments_md = rebuild_commitments_view(brain_dir)
    (views_dir / "commitments.md").write_text(commitments_md, encoding="utf-8")
    results["commitments"] = len(commitments_md)

    return results
