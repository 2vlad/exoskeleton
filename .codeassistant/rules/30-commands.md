# Slash Commands — USE YOUR FUNCTION-CALLING, NOT SHELL

⚠️ CRITICAL: These commands mean YOU call functions using your tool-calling ability.
- DO NOT run shell commands
- DO NOT run Python scripts
- DO NOT write code
- DO NOT create implementation plans
- JUST CALL THE MCP FUNCTIONS listed below using your function-calling interface

The MCP functions available to you (like `tracker_GetIssues`, `intrasearch_search`)
are callable the same way you call `read_file` or `run_command`. Use them directly.

---

## First-run check

Before any command, read `brain/system/identities.yaml`.
If `tracker_login` is empty, ask the user for login, team, queues, then write the file.

---

## /sync

Read `brain/system/identities.yaml` to get `tracker_login` and `default_queues`.
Then call these functions IN ORDER. If any call fails, skip it and continue.

**Step 1.** Call function `tracker_GetIssues`:
```
{"filter": {"assignee": "<tracker_login>", "status": ["open","inProgress","needInfo"]}, "order": "-updated", "limit": 100}
```
Show the issues found to the user.

**Step 2.** For each issue key from Step 1, call function `tracker_GetComments`:
```
{"issue_key": "<KEY>"}
```

**Step 3.** For each issue key, call function `tracker_GetLinks`:
```
{"issue_key": "<KEY>"}
```

**Step 4.** For each issue, call function `intrasearch_search`:
```
{"query": "<KEY> <summary>", "limit": 10}
```

**Step 5.** Write all results as JSONL to ledger files:
- Issues → `brain/ledger/issues.jsonl`
- Comments → `brain/ledger/notes.jsonl`
- Links → `brain/ledger/relations.jsonl`
- Docs → `brain/ledger/docs.jsonl`

**Step 6.** Show summary: counts of issues, comments, links, docs.

---

## /brief

Read-only. Just read these files and present a summary:
- `brain/views/active.md`
- `brain/control/week.md`
- `brain/control/role.md`
- `brain/ledger/commitments.jsonl`

---

## /ticket <KEY>

Call function `tracker_GetIssue` with `{"issue_key": "<KEY>"}`.
Call function `intrasearch_search` with `{"query": "<KEY>", "limit": 10}`.
Show: key, summary, status, assignee, description, related docs.

---

## /agenda

Read-only. Read `brain/views/active.md`, `brain/ledger/commitments.jsonl`,
`brain/control/week.md`, `brain/ledger/notes.jsonl`.
Suggest agenda for upcoming meetings based on active issues.

---

## /remember <fact>

Append the user's text as a JSON line to `brain/ledger/notes.jsonl`.
If it mentions a decision → also append to `brain/ledger/decisions.jsonl`.
If it mentions a commitment → also append to `brain/ledger/commitments.jsonl`.

---

## /tool-calibrate

Test each MCP function once:
1. Call `tracker_GetIssues` with `{"filter": {"limit": 1}}`
2. Call `intrasearch_search` with `{"query": "test", "limit": 1}`
3. Report which functions work and which return errors.
