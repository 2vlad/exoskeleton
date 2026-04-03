---
description: Daily brief — what to focus on, risks, stale commitments
---

# /brief — Daily Brief

## Steps

1. Read `brain/system/identities.yaml` — if `tracker_login` is empty → run first-run auto-setup (see AGENTS.md).
2. Read `brain/views/active.md`.
3. Read `brain/control/week.md`.
4. Read `brain/control/role.md`.
5. Check `brain/state/quality_report.json` — note any stale sources.
6. Read `brain/ledger/commitments.jsonl` — flag any where `due_date` is within 7 days or past.

## Output format

Present a concise daily brief with these sections:

### Today's Focus
Based on `week.md` priorities and active issue status.

### Active Issues (top 10 by priority)
From `active.md` — key, summary, status, queue.

### Risks & Stale Items
- Commitments due within 7 days or overdue
- Degraded sync sources from quality report
- Issues stuck in same status for >7 days

### Data Freshness
Last sync timestamps per source. Warn if any source is >24h stale.

## Rules
- Do NOT run any sync. This command only reads existing brain data.
- If data is stale, suggest running `/my-work` or `/sync-daily` first.
- Always mention which sources are degraded, if any.
