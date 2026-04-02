---
description: Build issue dossier from Tracker and related context
argument-hint: Issue key (e.g., PM-123)
---

# /issue — Issue Dossier

## Steps

1. Read `brain/system/query-recipes/tracker.yaml` recipe `get_issue_by_key`.
2. Substitute `{issue_key}` with the provided argument.
3. Execute the recipe (primary tool, then fallbacks).
4. Save raw response to `brain/ingest/raw/tracker_issue_{key}_{timestamp}.json`.
5. Normalize the issue.
6. Search for related context:
   a. `intrasearch.search` with the issue summary as query.
   b. `intrasearch.stsearch` with the issue key.
7. Normalize document hits.
8. Merge issue into `brain/ledger/issues.jsonl`.
9. Merge doc hits into `brain/ledger/docs.jsonl`.
10. Create relations in `brain/ledger/relations.jsonl`:
    - issue -> related docs (relation_type: "related_to")
    - issue -> assignee (relation_type: "assigned_to")
    - issue -> queue/project (relation_type: "belongs_to")
11. Rebuild relevant views.
12. Present the issue dossier:
    - Key, summary, status, assignee, queue, priority
    - Description (from payload)
    - Related docs (titles + URLs)
    - Related issues (from links in tracker response)
    - Relevant decisions/commitments from ledger

## Rules
- Issue facts (status, assignee) MUST come from tracker, not from intrasearch snippets.
- Doc hits are supporting context, not authoritative issue data.
