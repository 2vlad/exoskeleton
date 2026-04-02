# Runbook: Entity Collision / Ambiguous Alias

## Symptoms
- Two different entities resolve to the same alias
- A person/project name matches multiple entries in `aliases.yaml`
- Entity resolution returns multiple candidates

## Steps

1. **Do NOT auto-merge.** Ambiguous matches must be preserved as ambiguous.
2. Write unresolved entity to `brain/views/inbox.md` with:
   - The raw mention text
   - All candidate matches with context
   - Source and timestamp
3. Mark the ledger record's `entity_refs` as `["unresolved:<raw_text>"]`.
4. Human reviews `inbox.md` and resolves by:
   - Adding a more specific alias to `brain/system/aliases.yaml`
   - Manually editing the ledger record's `entity_refs`

## Prevention
- Keep `aliases.yaml` specific: use full names, logins, unique identifiers.
- Prefer tracker logins over display names for people.
- Prefer queue keys over project display names.
