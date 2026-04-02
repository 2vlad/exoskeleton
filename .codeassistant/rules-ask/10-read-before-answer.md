---
description: Always read brain context before answering questions
globs: ["brain/**"]
alwaysApply: true
---

# Read Before Answer

Before answering any question about the user's work, projects, or team:

1. Read `brain/views/active.md` for current work context.
2. Read `brain/control/week.md` for current priorities.
3. Check `brain/state/quality_report.json` for data freshness.
4. If data is stale (>24h), suggest running `/sync-daily` first.
5. If the question is about a specific project, read `brain/views/projects/<slug>.md`.
6. If the question is about a person, read `brain/views/people/<slug>.md`.
