---
description: Suggest agenda for the next 2 upcoming calls
argument-hint: Optional — person name or meeting topic to filter
---

# /agenda — Meeting Agenda

## Steps

1. Read `brain/system/identities.yaml` — if `tracker_login` is empty → run first-run auto-setup (see AGENTS.md).
2. Read `brain/views/active.md` — current issues and their status.
3. Read `brain/ledger/commitments.jsonl` — open commitments, especially overdue or due soon.
4. Read `brain/ledger/decisions.jsonl` — recent decisions that may need follow-up.
5. Read `brain/control/week.md` — this week's focus and priorities.
6. Read `brain/ledger/notes.jsonl` — recent notes that mention meetings or people.
7. If the user specified a person or topic, filter context to that scope.
8. Identify the 2 nearest upcoming calls:
   a. Look for commitments/notes mentioning meetings, syncs, stand-ups, 1:1s.
   b. Check entity_refs for people involved.
   c. If calendar data is not available, ask the user who the next 2 calls are with.
9. For each call, generate an agenda:
   - **Topics to raise** — blocked issues, decisions needed, status updates relevant to attendees.
   - **Questions to ask** — open items where attendees have context.
   - **Commitments to follow up** — things promised by or to attendees.
   - **FYI items** — recent changes attendees should know about.

## Output format

### Call 1: [meeting name / person]

**Topics to raise:**
- ...

**Questions to ask:**
- ...

**Follow up on commitments:**
- ...

**FYI:**
- ...

### Call 2: [meeting name / person]

(same structure)

## Rules
- Do NOT invent agenda items. Only use data from ledger, views, and control files.
- If there's not enough context about upcoming calls, ask the user who the calls are with.
- Keep each agenda concise — 3-5 items per section max.
- Prioritize: blocked items > overdue commitments > status updates > FYI.
