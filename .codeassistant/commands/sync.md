---
description: Full sync — issues, comments, links, wiki, goals, calendar
argument-hint: Optional queue filter (e.g., PM, LUMI)
---

# /sync — Full Sync

## Overview

Syncs all data sources in sequence. Each phase is independent — if one fails, the rest continue.

## Phase 1: Issues

1. Read `brain/system/identities.yaml` to get `tracker_login` and `default_queues`.
   - If `tracker_login` is empty → run first-run auto-setup (see AGENTS.md), then continue.
2. Read `brain/system/query-recipes/tracker.yaml` recipe `my_open_issues`.
3. If recipe is not calibrated, warn the user and suggest `/tool-calibrate` first.
4. Execute the recipe (substitute `{tracker_login}`; follow fallback chain on failure).
5. Save raw response to `brain/ingest/raw/tracker_issues_{timestamp}.json`.
6. Normalize each issue (`scripts/normalize.py`):
   - Extract key, summary, status, assignee, queue, priority, dates.
   - Set `source: "tracker"`, `confidence: "canonical"`, `dedupe_key: "tracker:{key}"`.
7. Merge into `brain/ledger/issues.jsonl` (upsert by dedupe_key).

## Phase 2: Comments on active issues

For each issue from Phase 1 (or from existing `brain/ledger/issues.jsonl` if Phase 1 failed):
1. Execute recipe `issue_comments` with `{issue_key}`.
2. Save raw to `brain/ingest/raw/tracker_comments_{key}_{timestamp}.json`.
3. Normalize: extract id, text, author, date.
   - Set `dedupe_key: "comment:{issue_key}:{comment_id}"`.
4. Merge into `brain/ledger/notes.jsonl`.
5. Scan comment text for decisions and commitments (Tier A extraction).

## Phase 3: Linked issues (dependency graph)

For each issue from Phase 1:
1. Execute recipe `issue_links` with `{issue_key}`.
2. Normalize each link: direction (inward/outward), type (blocks/depends/relates), target key.
3. Merge into `brain/ledger/relations.jsonl`:
   - `dedupe_key: "link:{issue_key}:{direction}:{type}:{target_key}"`.
4. Highlight blockers — issues where link type is "blocks" and target is in user's queues.

## Phase 4: Wiki pages

For each active issue:
1. Execute recipe `wiki_by_issue` with `{issue_key}` and `{issue_summary}`.
2. Normalize doc hits: title, url, snippet.
   - Set `dedupe_key: "wiki:{url}"`, `confidence: "corroborated"`.
3. Merge into `brain/ledger/docs.jsonl`.
4. Create relations: issue → doc (`relation_type: "documented_in"`).

## Phase 5: Goals hierarchy

1. Execute recipe `goals_hierarchy` for user's default queues.
2. Normalize goals: key, summary, type (year/quarter/sprint), parent, children, progress.
   - Set `dedupe_key: "goal:{key}"`.
3. Merge into `brain/ledger/issues.jsonl` (goals are issues with type=goal).
4. Create relations: goal → child goals/issues (`relation_type: "parent_of"`).
5. Build hierarchy: year goals → quarter goals → sprint goals → issues.

## Phase 6: Calendar (next 2 days)

1. Execute recipe `upcoming_events` from `calendar.yaml`.
2. If calendar MCP is not available, skip with a warning.
3. Normalize events: id, name, start, end, attendees.
   - Set `dedupe_key: "cal:{event_id}"`.
4. Merge into `brain/ledger/notes.jsonl` with `kind: "calendar_event"`.
5. Cross-reference attendees with `brain/system/org_structure.md` and `aliases.yaml`.

## Post-sync

1. Run quality checks (`scripts/sync_quality.py`).
2. If quality passes → rebuild all views via `scripts/rebuild_views.py`.
3. If quality fails → keep previous views, log to `brain/ingest/failed/`.
4. Log sync run to `brain/ledger/sync_runs.jsonl` with per-phase stats.
5. Display summary: issues synced, comments found, blockers, upcoming events, goal progress.

## Validation rules
- Every issue must have key, summary, status.
- Keys must match pattern `[A-Z][A-Z0-9]+-\d+`.
- If zero issues found and ledger has existing issues, do NOT delete them.
- Mark sync as `partial` if any phase failed or any fallback was used.
- Each phase logs its own status independently.

## On failure
- Follow runbook: `brain/system/runbooks/empty-tracker-response.md`.
- If a single phase fails, continue with remaining phases.
- Report per-phase success/failure in the summary.
