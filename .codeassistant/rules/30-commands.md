# Slash Commands

When the user types one of these commands, follow the instructions exactly.

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

Full data sync. Read `.codeassistant/commands/sync.md` for detailed steps.

Short version:
1. Read `brain/system/identities.yaml` → get `tracker_login`, `default_queues`
2. Read `brain/system/query-recipes/tracker.yaml` → get recipe `my_open_issues`
3. Call tracker MCP tool to get issues for the user (substitute `tracker_login` in recipe args)
4. For each issue: get comments, get linked issues
5. Search wiki for related docs via intrasearch
6. Get goals from tracker
7. Get calendar events (if available)
8. Save all results to `brain/ledger/*.jsonl`
9. Show the user a summary of what was synced

**Important:** if a tool call fails, skip that phase and continue with the next one.

---

## /brief

Daily briefing. Read-only — do NOT sync.

1. Read `brain/views/active.md`
2. Read `brain/control/week.md`
3. Read `brain/control/role.md`
4. Read `brain/ledger/commitments.jsonl`
5. Present: today's focus, top issues, risks, data freshness
6. If data is stale, suggest running `/sync`

---

## /ticket <KEY>

Ticket dossier. Example: `/ticket PM-123`

1. Call tracker MCP to get the issue by key
2. Search intrasearch for related wiki docs
3. Save to ledger
4. Present: key, summary, status, assignee, description, related docs, related issues

---

## /agenda

Meeting agenda for next 2 calls.

1. Read `brain/views/active.md`, `brain/ledger/commitments.jsonl`, `brain/control/week.md`
2. Check `brain/ledger/notes.jsonl` for calendar events
3. If no calendar events found, ask the user who the next 2 calls are with
4. For each call: suggest topics, questions, follow-ups, FYIs based on active issues and commitments
5. Read `brain/system/org_structure.md` to understand attendees' roles

---

## /remember <fact>

Store a note.

1. Take the user's text
2. Extract issue keys, dates, URLs from the text
3. Create a Note record in `brain/ledger/notes.jsonl`
4. If text contains decision language ("decided", "agreed") → also create Decision in `brain/ledger/decisions.jsonl`
5. If text contains commitment language ("will do", "by <date>") → also create Commitment in `brain/ledger/commitments.jsonl`
6. Confirm what was stored

---

## /tool-calibrate

Test MCP tool connections.

1. Read `brain/system/identities.yaml`
2. Read each recipe in `brain/system/query-recipes/`
3. For each recipe: substitute template vars, call the tool, record if it worked
4. Update recipe files with `calibrated: true/false`
5. Report results
