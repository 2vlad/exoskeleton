---
description: Plan sync operations before executing them
globs: ["brain/**", "scripts/**"]
alwaysApply: true
---

# Plan Before Writing to Brain

Before any write operation to the brain:

1. Identify the sync recipe in `brain/system/query-recipes/`.
2. Verify the recipe is calibrated (`calibrated: true`).
3. Plan which ledger files will be affected.
4. Confirm the routing rules in `scripts/routing.py` match your intent.
5. Only then execute the sync.

Never skip straight to writing ledger records without knowing:
- Which source you're querying
- What the expected output schema looks like
- Where the records will be routed
- What validation will run after merge
