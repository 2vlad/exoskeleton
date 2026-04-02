# Runbook: Tracker Returns Empty or Unexpected Response

## Symptoms
- `GetIssues` returns 0 results when user expects issues
- Response is structurally invalid (missing expected fields)
- Timeout or connection error

## Steps

1. **Do NOT delete existing issue data.** Keep previous `brain/ledger/issues.jsonl` intact.
2. Retry once with narrower filter (e.g., single queue instead of all default_queues).
3. If still empty, fall back to `intrasearch.stsearch` with query `assignee:{tracker_login} status:open`.
4. If stsearch returns candidate issue keys, rehydrate each via `tracker.GetIssue` per key.
5. If all fallbacks fail:
   - Mark sync run as `partial` in `brain/ledger/sync_runs.jsonl`.
   - Add warning to `brain/state/quality_report.json`: `"tracker retrieval degraded"`.
   - Surface degraded status in `brain/views/active.md` header.
6. **Never silently succeed with zero results when prior state exists.**

## Prevention
- Run `/tool-calibrate` to verify tracker recipes work with current MCP state.
- Check that `brain/system/identities.yaml` has correct `tracker_login`.
