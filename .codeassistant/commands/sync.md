---
description: Sync and show current work items from Tracker
argument-hint: Optional queue filter (e.g., PM, LUMI)
---

# /sync — Sync Current Work

## Steps

1. Read `brain/system/identities.yaml` to get `tracker_login` and `default_queues`.
   - If `tracker_login` is empty → run first-run auto-setup (see AGENTS.md), then continue.
2. Read `brain/system/query-recipes/tracker.yaml` recipe `my_open_issues`.
3. If recipe is not calibrated, warn the user and suggest `/tool-calibrate` first.
4. Execute the recipe:
   a. Call the primary tool with the templated args (substitute `{tracker_login}`).
   b. If it fails or returns empty, follow the fallback chain.
5. Save raw response to `brain/ingest/raw/tracker_my_work_{timestamp}.json`.
6. Normalize each issue using the pattern from `scripts/normalize.py`:
   - Extract key, summary, status, assignee, queue, priority, dates.
   - Set `source: "tracker"`, `confidence: "canonical"`, `dedupe_key: "tracker:{key}"`.
7. Merge normalized issues into `brain/ledger/issues.jsonl` (upsert by dedupe_key).
8. Run quality checks.
9. If quality passes, rebuild `brain/views/active.md`.
10. If quality fails, keep previous views and report the failure.
11. Log sync run to `brain/ledger/sync_runs.jsonl`.
12. Display the updated active issues to the user.

## Validation rules
- Every issue must have key, summary, status.
- Keys must match pattern `[A-Z][A-Z0-9]+-\d+`.
- If zero issues found and ledger has existing issues, do NOT delete them.
- Mark sync as `partial` if any fallback was used.

## On failure
- Follow runbook: `brain/system/runbooks/empty-tracker-response.md`.
