---
description: Store an explicit fact or note into brain memory
argument-hint: The fact to remember (e.g., "We decided to delay the launch to Q3")
---

# /remember — Store Human Input

## Steps

1. Take the user's input text.
2. Use Tier A extraction (`scripts/extract.py`) to find:
   - Issue keys mentioned
   - Dates mentioned
   - URLs mentioned
   - People/project references (resolve via `brain/system/aliases.yaml`)
3. Create a Note record:
   - `id`: `manual:note_{timestamp}`
   - `source`: `manual`
   - `source_ref`: `user-input`
   - `kind`: `note`
   - `text`: the full user input
   - `entity_refs`: resolved references from step 2
   - `confidence`: `canonical` (human input is high-intent)
   - `dedupe_key`: `manual:note_{hash_of_text}`
4. If the text contains decision language ("we decided", "decision:", "agreed to"):
   - Also create a Decision record with `confidence: canonical`.
5. If the text contains commitment language ("will do", "committed to", "by [date]"):
   - Also create a Commitment record.
6. Merge all records into appropriate ledger files.
7. Run quality checks.
8. Rebuild relevant views.
9. Confirm to user what was stored and where.

## Rules
- Never paraphrase the user's input. Store the exact text.
- Entity resolution failures go to `brain/views/inbox.md` as unresolved.
- If you're unsure whether something is a decision vs commitment vs note, store it as a note.
