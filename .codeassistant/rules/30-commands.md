# Slash Commands

**IMPORTANT: These are OPERATIONAL commands, NOT coding tasks.**
When the user types a slash command, you must EXECUTE it immediately using MCP tools.
Do NOT write code, scripts, or implementation plans. Just DO it.

## First-run check (applies to ALL commands)

Before executing any command, read `brain/system/identities.yaml`.
If `tracker_login` is empty, run first-run setup:
1. Ask the user: "Какой у тебя логин? (например ivpetrov)"
2. Ask: "Какая команда? (например practicum)"
3. Ask: "Какие очереди трекера? (например PRACT,LUMI)"
4. Write `brain/system/identities.yaml` with the answers:
```yaml
user:
  display_name: ""
  tracker_login: "<login>"
  email: "<login>@yandex-team.ru"
  staff_login: "<login>"
  teams: ["<team>"]
  default_queues: ["<queue1>", "<queue2>"]
```
5. Then continue with the original command.

---

## /sync

**DO:** Call MCP tools to fetch real data. **DON'T:** Write code or scripts.

Steps:
1. Read `brain/system/identities.yaml` → get `tracker_login`, `default_queues`.
2. Call tracker MCP tool (`tracker.GetIssues`) with args:
   ```json
   {"filter": {"assignee": "<tracker_login>", "status": ["open", "inProgress", "needInfo"]}, "order": "-updated", "limit": 100}
   ```
3. Show the user the issues found.
4. For each issue, call `tracker.GetComments` with `{"issue_key": "<KEY>"}`.
5. For each issue, call `tracker.GetLinks` with `{"issue_key": "<KEY>"}`.
6. Search wiki: call `intrasearch.search` with `{"query": "<issue_key> <summary>", "limit": 10}`.
7. Write results as JSONL lines to the appropriate ledger files:
   - Issues → `brain/ledger/issues.jsonl`
   - Comments → `brain/ledger/notes.jsonl`
   - Links → `brain/ledger/relations.jsonl`
   - Wiki docs → `brain/ledger/docs.jsonl`
8. Show summary: how many issues, comments, links, docs found.

**If a tool call fails, skip it and move to the next step. Never stop the whole sync because one tool failed.**

---

## /brief

**Read-only — just read files and present info. Do NOT call any MCP tools.**

1. Read `brain/views/active.md`
2. Read `brain/control/week.md`
3. Read `brain/control/role.md`
4. Read `brain/ledger/commitments.jsonl`
5. Present: today's focus, top issues, risks, data freshness
6. If data is stale, suggest running `/sync`

---

## /ticket <KEY>

**DO:** Call MCP tools with the specific issue key. **DON'T:** Write code.

1. Call `tracker.GetIssue` with `{"issue_key": "<KEY>"}`
2. Call `intrasearch.search` with `{"query": "<KEY>", "limit": 10}`
3. Show the user: key, summary, status, assignee, description, related docs

---

## /agenda

Meeting agenda for next 2 calls.

1. Read `brain/views/active.md`, `brain/ledger/commitments.jsonl`, `brain/control/week.md`
2. Check `brain/ledger/notes.jsonl` for calendar events
3. If no calendar events, ask the user who the next 2 calls are with
4. For each call: suggest topics, questions, follow-ups based on active issues
5. Read `brain/system/org_structure.md` to understand attendees' roles

---

## /remember <fact>

1. Take the user's text exactly as written
2. Append a JSON line to `brain/ledger/notes.jsonl` with the text
3. If the text mentions a decision → also append to `brain/ledger/decisions.jsonl`
4. If the text mentions a commitment → also append to `brain/ledger/commitments.jsonl`
5. Confirm what was stored

---

## /tool-calibrate

**DO:** Call each MCP tool once to test it works. **DON'T:** Write code.

1. Read `brain/system/identities.yaml`
2. Try calling `tracker.GetIssues` with a simple filter
3. Try calling `intrasearch.search` with a test query
4. Report which tools work and which don't
