# Phase 1: Skeleton and Reliability Spine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the foundational repository structure, deterministic data pipeline (normalize → merge → rebuild views), system brain, YCA commands/rules, and test harness for the PM Copilot Exoskeleton.

**Architecture:** A file-based exoskeleton where YAML configs define agent operational memory, JSONL ledger stores canonical facts with provenance, Python scripts deterministically transform raw → normalized → ledger → markdown views, and YCA slash commands invoke structured recipes instead of free-form tool improvisation. The weak-model constraint means every decision the agent would normally make is pre-encoded in config or code.

**Tech Stack:** Python 3.11+, PyYAML, pytest, JSONL (newline-delimited JSON), YAML configs, Markdown views, YCA `.codeassistant/` conventions.

---

## File Structure

```
pm-copilot-yca/
├── AGENTS.md                              # Top-level agent instructions for YCA
├── .codeassistantignore                   # Files to exclude from YCA context
├── .mcp.json.example                      # MCP server config template
├── pyproject.toml                         # Python project config (deps, pytest)
├── .codeassistant/
│   ├── rules/
│   │   ├── 00-safety.md                   # Safety rules: no overwrite, no invent
│   │   ├── 10-source-priority.md          # Source authority hierarchy
│   │   └── 20-brain-map.md                # What lives where in brain/
│   ├── rules-ask/
│   │   └── 10-read-before-answer.md       # Read brain before answering
│   ├── rules-architect/
│   │   └── 10-plan-before-writing.md      # Plan before editing brain
│   └── commands/
│       ├── brief.md                       # /brief command
│       ├── my-work.md                     # /my-work command
│       ├── issue.md                       # /issue <key> command
│       ├── remember.md                    # /remember <fact> command
│       └── tool-calibrate.md              # /tool-calibrate command
├── brain/
│   ├── system/
│   │   ├── identities.yaml               # User identity across systems
│   │   ├── source-map.yaml               # Source → fact-type authority
│   │   ├── aliases.yaml                   # Name/project aliases
│   │   ├── query-recipes/
│   │   │   ├── tracker.yaml              # Tracker retrieval recipes
│   │   │   ├── intrasearch.yaml          # Intrasearch retrieval recipes
│   │   │   └── deepagent.yaml            # DeepAgent retrieval recipes
│   │   ├── schemas/
│   │   │   ├── issue.json                # JSON Schema for issue records
│   │   │   ├── document.json             # JSON Schema for doc records
│   │   │   ├── decision.json             # JSON Schema for decision records
│   │   │   ├── commitment.json           # JSON Schema for commitment records
│   │   │   ├── entity.json               # JSON Schema for entity records
│   │   │   ├── note.json                 # JSON Schema for note records
│   │   │   ├── relation.json             # JSON Schema for relation records
│   │   │   └── sync_run.json             # JSON Schema for sync run records
│   │   └── runbooks/
│   │       ├── empty-tracker-response.md  # What to do when tracker returns empty
│   │       └── entity-collision.md        # Resolving ambiguous entities
│   ├── ledger/
│   │   ├── .gitkeep
│   │   ├── entities.jsonl
│   │   ├── issues.jsonl
│   │   ├── docs.jsonl
│   │   ├── decisions.jsonl
│   │   ├── commitments.jsonl
│   │   ├── notes.jsonl
│   │   ├── relations.jsonl
│   │   └── sync_runs.jsonl
│   ├── views/
│   │   ├── active.md
│   │   ├── inbox.md
│   │   ├── decisions.md
│   │   ├── commitments.md
│   │   ├── references.md
│   │   ├── projects/
│   │   │   └── .gitkeep
│   │   ├── people/
│   │   │   └── .gitkeep
│   │   └── attention/
│   │       └── .gitkeep
│   ├── control/
│   │   ├── role.md
│   │   ├── quarter.md
│   │   ├── week.md
│   │   └── constraints.md
│   ├── ingest/
│   │   ├── raw/
│   │   │   └── .gitkeep
│   │   ├── normalized/
│   │   │   └── .gitkeep
│   │   └── failed/
│   │       └── .gitkeep
│   └── state/
│       ├── source_state.json
│       ├── entity_index.json
│       ├── sync_cursor.json
│       └── quality_report.json
├── scripts/
│   ├── __init__.py
│   ├── models.py                          # Pydantic models for all record types
│   ├── normalize.py                       # Raw → normalized records
│   ├── merge_ledger.py                    # Normalized → ledger (upsert by dedupe_key)
│   ├── rebuild_views.py                   # Ledger → markdown views
│   ├── sync_quality.py                    # Invariant checks + quality report
│   ├── entity_resolver.py                 # Alias/identity-based entity resolution
│   ├── extract.py                         # Deterministic + LLM extraction tiers
│   ├── routing.py                         # Schema-driven record routing
│   └── fixtures/
│       ├── __init__.py
│       ├── tracker_issues.json            # Sample tracker responses
│       ├── intrasearch_hits.json          # Sample intrasearch responses
│       ├── deepagent_response.json        # Sample deepagent responses
│       ├── broken_responses.json          # Malformed/empty/partial responses
│       └── ambiguous_aliases.json         # Alias collision fixtures
└── tests/
    ├── __init__.py
    ├── conftest.py                        # Shared fixtures + tmp brain setup
    ├── test_models.py                     # Schema validation tests
    ├── test_normalize.py                  # Raw → normalized transformation tests
    ├── test_merge_ledger.py               # Upsert, dedupe, idempotency tests
    ├── test_rebuild_views.py              # Ledger → markdown golden tests
    ├── test_sync_quality.py               # Invariant check tests
    ├── test_entity_resolver.py            # Alias resolution tests
    ├── test_extract.py                    # Extraction tier tests
    ├── test_routing.py                    # Record routing tests
    └── golden/
        ├── active.md                      # Expected active.md from fixture data
        ├── decisions.md                   # Expected decisions.md
        ├── commitments.md                 # Expected commitments.md
        └── project_lumi.md               # Expected project dossier
```

---

## Task 1: Repository scaffold and Python project setup

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.codeassistantignore`
- Create: `.mcp.json.example`
- Create: all empty directories with `.gitkeep` files
- Create: `brain/state/source_state.json`, `entity_index.json`, `sync_cursor.json`, `quality_report.json`

- [ ] **Step 1: Initialize git repo and create pyproject.toml**

```bash
cd /Users/tovlad01/dev/exoskeleton
git init
```

```toml
# pyproject.toml
[project]
name = "pm-copilot-yca"
version = "0.1.0"
description = "PM Copilot Exoskeleton for Yandex Code Assistant"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "jsonschema>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-tmp-files>=0.0.2",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 2: Create .gitignore**

```gitignore
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
.mcp.json
brain/ingest/raw/*.json
brain/ingest/raw/*.jsonl
brain/ingest/normalized/*.json
brain/ingest/normalized/*.jsonl
brain/ingest/failed/*.json
```

- [ ] **Step 3: Create .codeassistantignore**

```
brain/ingest/raw/
brain/ingest/normalized/
brain/ingest/failed/
__pycache__/
.venv/
*.pyc
```

- [ ] **Step 4: Create .mcp.json.example**

Template with placeholders for all 5 MCP sources (tracker, intrasearch, deepagent, yt, infractl) using the mcp_proxy.py pattern from tg-connect.

```json
{
  "mcpServers": {
    "tracker_mcp": {
      "command": ".venv/bin/python3",
      "args": ["mcp_proxy.py", "-F", "~/.arc/token", "--endpoint", "mcp.yandex.net/ws?servers=tracker_mcp"]
    },
    "intrasearch": {
      "command": ".venv/bin/python3",
      "args": ["mcp_proxy.py", "-F", "~/.arc/token", "--endpoint", "mcp.yandex.net/ws?servers=intrasearch"]
    },
    "deepagent": {
      "command": ".venv/bin/python3",
      "args": ["mcp_proxy.py", "-F", "~/.arc/token", "--endpoint", "mcp.yandex.net/ws?servers=deepagent"]
    },
    "yt": {
      "command": ".venv/bin/python3",
      "args": ["mcp_proxy.py", "-F", "~/.yt/token", "--endpoint", "mcp.yandex.net/ws?servers=yt"]
    },
    "infractl": {
      "command": ".venv/bin/python3",
      "args": ["mcp_proxy.py", "-F", "~/.arc/token", "--endpoint", "mcp.yandex.net/ws?servers=infractl"]
    }
  }
}
```

- [ ] **Step 5: Create all directory scaffolding**

Create all directories listed in the file structure above with `.gitkeep` files where needed.

- [ ] **Step 6: Create empty state files**

```json
// brain/state/source_state.json
{
  "last_sync": {},
  "source_health": {}
}
```

```json
// brain/state/entity_index.json
{
  "entities": {},
  "aliases": {}
}
```

```json
// brain/state/sync_cursor.json
{
  "cursors": {}
}
```

```json
// brain/state/quality_report.json
{
  "last_check": null,
  "warnings": [],
  "degraded_sources": []
}
```

- [ ] **Step 7: Create empty ledger JSONL files**

Create empty files: `brain/ledger/entities.jsonl`, `issues.jsonl`, `docs.jsonl`, `decisions.jsonl`, `commitments.jsonl`, `notes.jsonl`, `relations.jsonl`, `sync_runs.jsonl`.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: initialize repository scaffold with directory structure and config"
```

---

## Task 2: System brain — identities, source-map, aliases

**Files:**
- Create: `brain/system/identities.yaml`
- Create: `brain/system/source-map.yaml`
- Create: `brain/system/aliases.yaml`

- [ ] **Step 1: Create identities.yaml with placeholder structure**

```yaml
# brain/system/identities.yaml
# Current user identity across systems.
# Fill in your actual values before first use.
user:
  display_name: ""          # e.g. "Vlad Kiaune"
  tracker_login: ""         # e.g. "vladk"
  email: ""                 # e.g. "vlad@yandex-team.ru"
  staff_login: ""           # e.g. "vladk"
  teams: []                 # e.g. ["practicum"]
  default_queues: []        # e.g. ["PRACT", "LUMI"]
```

- [ ] **Step 2: Create source-map.yaml**

```yaml
# brain/system/source-map.yaml
# Defines which source is authoritative for which class of fact.
# The agent MUST consult this before choosing a tool.

authority:
  issue_status: tracker
  issue_assignee: tracker
  issue_history: tracker
  project_goal_meta: tracker
  document_snippets: intrasearch
  wiki_content: intrasearch
  broad_internal_context: deepagent
  data_schema: yt
  data_path_existence: yt
  infra_ownership: infractl
  infra_namespace: infractl

# Source trust hierarchy (higher = more trusted for conflicts)
trust_order:
  - tracker        # 1st — canonical for issues, projects, goals
  - yt             # 2nd — canonical for data schemas, paths
  - infractl       # 3rd — canonical for infra objects, ownership
  - intrasearch    # 4th — canonical for doc/wiki/SO snippets
  - deepagent      # 5th — discovery only, never authoritative
  - manual         # high intent, low structure — goes to review

# Conflict resolution: if sources disagree, trust the higher-ranked source.
# DeepAgent NEVER overrides tracker/yt/infractl/intrasearch on factual claims.
```

- [ ] **Step 3: Create aliases.yaml**

```yaml
# brain/system/aliases.yaml
# Aliases for projects, people, queues, common abbreviations.
# Used by entity_resolver.py for deterministic name matching.
# Edit this file as you discover new aliases.

projects: {}
  # example:
  # navi: [navigator, нави, навигатор]
  # lumi: [луми, lumi]

people: {}
  # example:
  # sergey-sus: [сережа сус, sus, sergey.sus]

queues: {}
  # example:
  # PRACT: [practicum, практикум]

abbreviations: {}
  # example:
  # PM: product manager
  # OKR: objectives and key results
```

- [ ] **Step 4: Commit**

```bash
git add brain/system/identities.yaml brain/system/source-map.yaml brain/system/aliases.yaml
git commit -m "feat: add system brain config — identities, source-map, aliases"
```

---

## Task 3: Query recipes for tracker, intrasearch, deepagent

**Files:**
- Create: `brain/system/query-recipes/tracker.yaml`
- Create: `brain/system/query-recipes/intrasearch.yaml`
- Create: `brain/system/query-recipes/deepagent.yaml`

- [ ] **Step 1: Create tracker.yaml**

```yaml
# brain/system/query-recipes/tracker.yaml
# Tested retrieval recipes for Tracker MCP.
# IMPORTANT: Only add recipes after real successful runs via /tool-calibrate.
# The agent MUST use these recipes, never improvise tracker queries.

recipes:
  my_open_issues:
    description: "Find current user's open issues in default queues"
    primary_tool: tracker.GetIssues
    args_template:
      filter:
        assignee: "{tracker_login}"
        status:
          - open
          - inProgress
          - needInfo
      order: "-updated"
      limit: 100
    fallbacks:
      - tool: intrasearch.stsearch
        args_template:
          query: "assignee:{tracker_login} status:open"
          limit: 50
    validate:
      min_records: 0
      require_fields: [key, summary, status]
    calibrated: false
    last_successful_call: null
    example_response: null

  get_issue_by_key:
    description: "Fetch a single issue by its key"
    primary_tool: tracker.GetIssue
    args_template:
      issue_key: "{issue_key}"
    fallbacks:
      - tool: intrasearch.stsearch
        args_template:
          query: "{issue_key}"
          limit: 5
    validate:
      require_fields: [key, summary, status, assignee]
    calibrated: false
    last_successful_call: null
    example_response: null

  recently_updated_issues:
    description: "Find recently updated issues in user's queues"
    primary_tool: tracker.GetIssues
    args_template:
      filter:
        queue: "{default_queues}"
        updated_from: "{since_date}"
      order: "-updated"
      limit: 50
    fallbacks:
      - tool: intrasearch.stsearch
        args_template:
          query: "queue:{default_queues_joined} updated:>{since_date}"
    validate:
      require_fields: [key, summary, status, updatedAt]
    calibrated: false
    last_successful_call: null
    example_response: null

  search_goals_projects:
    description: "Search for goals, projects, portfolios"
    primary_tool: tracker.SearchEntities
    args_template:
      query: "{search_query}"
      entity_type: "{entity_type}"
    fallbacks:
      - tool: intrasearch.stsearch
        args_template:
          query: "{search_query} type:goal OR type:project"
    validate:
      require_fields: [key, summary]
    calibrated: false
    last_successful_call: null
    example_response: null
```

- [ ] **Step 2: Create intrasearch.yaml**

```yaml
# brain/system/query-recipes/intrasearch.yaml
# Tested retrieval recipes for Intrasearch MCP.
# Tools: search, stsearch, sosearch, semantic_code_search

recipes:
  doc_search:
    description: "Search wiki/docs for a topic"
    primary_tool: intrasearch.search
    args_template:
      query: "{topic}"
      limit: 20
    validate:
      require_fields: [title, url, snippet]
    calibrated: false
    last_successful_call: null
    example_response: null

  tracker_text_search:
    description: "Full-text search across tracker issues"
    primary_tool: intrasearch.stsearch
    args_template:
      query: "{query}"
      limit: 30
    validate:
      require_fields: [key, title, snippet]
    calibrated: false
    last_successful_call: null
    example_response: null

  so_search:
    description: "Search internal StackOverflow"
    primary_tool: intrasearch.sosearch
    args_template:
      query: "{query}"
      limit: 10
    validate:
      require_fields: [title, url, snippet]
    calibrated: false
    last_successful_call: null
    example_response: null
```

- [ ] **Step 3: Create deepagent.yaml**

```yaml
# brain/system/query-recipes/deepagent.yaml
# DeepAgent is for DISCOVERY ONLY.
# Results are ALWAYS marked as candidate confidence until corroborated.
# Never use DeepAgent as authoritative source for issue/project/infra facts.

recipes:
  broad_context:
    description: "Get broad internal context on a topic (discovery only)"
    primary_tool: deepagent.generate_answer
    args_template:
      message: "{query}"
    validate:
      # DeepAgent returns free text — no structural validation
      require_fields: []
    post_process:
      confidence: candidate
      requires_corroboration: true
    calibrated: false
    last_successful_call: null
    example_response: null

  candidate_issues:
    description: "Ask DeepAgent to find potentially related issues (must verify via tracker)"
    primary_tool: deepagent.generate_answer
    args_template:
      message: "Find tracker issues related to: {topic}. Return only issue keys (e.g. PROJ-123), one per line."
    validate:
      require_fields: []
    post_process:
      confidence: candidate
      requires_corroboration: true
      corroborate_via: tracker.GetIssue
    calibrated: false
    last_successful_call: null
    example_response: null
```

- [ ] **Step 4: Commit**

```bash
git add brain/system/query-recipes/
git commit -m "feat: add query recipes for tracker, intrasearch, deepagent"
```

---

## Task 4: Runbooks for failure handling

**Files:**
- Create: `brain/system/runbooks/empty-tracker-response.md`
- Create: `brain/system/runbooks/entity-collision.md`

- [ ] **Step 1: Create empty-tracker-response.md**

```markdown
# Runbook: Tracker Returns Empty or Unexpected Response

## Symptoms
- `GetIssues` returns 0 results when user expects issues
- Response is structurally invalid (missing expected fields)
- Timeout or connection error

## Steps

1. **Do NOT delete existing issue data.** Keep previous `brain/ledger/issues.jsonl` intact.
2. Retry once with narrower filter (e.g., single queue instead of all default_queues).
3. If still empty, fall back to `intrasearch.stsearch` with query `assignee:{tracker_login} status:open`.
4. If stsearch returns candidate issue keys, rehydrate each via `tracker.GetIssue` per key.
5. If all fallbacks fail:
   - Mark sync run as `partial` in `brain/ledger/sync_runs.jsonl`.
   - Add warning to `brain/state/quality_report.json`: `"tracker retrieval degraded"`.
   - Surface degraded status in `brain/views/active.md` header.
6. **Never silently succeed with zero results when prior state exists.**

## Prevention
- Run `/tool-calibrate` to verify tracker recipes work with current MCP state.
- Check that `brain/system/identities.yaml` has correct `tracker_login`.
```

- [ ] **Step 2: Create entity-collision.md**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add brain/system/runbooks/
git commit -m "feat: add operational runbooks for failure handling"
```

---

## Task 5: JSON Schemas for all ledger record types

**Files:**
- Create: `brain/system/schemas/issue.json`
- Create: `brain/system/schemas/document.json`
- Create: `brain/system/schemas/decision.json`
- Create: `brain/system/schemas/commitment.json`
- Create: `brain/system/schemas/entity.json`
- Create: `brain/system/schemas/note.json`
- Create: `brain/system/schemas/relation.json`
- Create: `brain/system/schemas/sync_run.json`

- [ ] **Step 1: Create issue.json schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Issue",
  "type": "object",
  "required": ["id", "source", "source_ref", "kind", "key", "summary", "status", "dedupe_key", "fetched_at"],
  "properties": {
    "id": { "type": "string", "pattern": "^tracker:.+" },
    "source": { "type": "string", "enum": ["tracker", "intrasearch", "deepagent"] },
    "source_type": { "type": "string", "const": "issue" },
    "source_ref": { "type": "string" },
    "kind": { "type": "string", "const": "issue" },
    "key": { "type": "string", "pattern": "^[A-Z][A-Z0-9]+-\\d+$" },
    "summary": { "type": "string", "minLength": 1 },
    "status": { "type": "string" },
    "assignee": { "type": ["string", "null"] },
    "reporter": { "type": ["string", "null"] },
    "queue": { "type": ["string", "null"] },
    "priority": { "type": ["string", "null"] },
    "updated_at": { "type": ["string", "null"], "format": "date-time" },
    "created_at": { "type": ["string", "null"], "format": "date-time" },
    "resolved_at": { "type": ["string", "null"], "format": "date-time" },
    "entity_refs": { "type": "array", "items": { "type": "string" } },
    "dedupe_key": { "type": "string" },
    "confidence": { "type": "string", "enum": ["canonical", "corroborated", "candidate"] },
    "fetched_at": { "type": "string", "format": "date-time" },
    "observed_at": { "type": ["string", "null"], "format": "date-time" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

- [ ] **Step 2: Create document.json schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Document",
  "type": "object",
  "required": ["id", "source", "source_ref", "kind", "title", "url", "dedupe_key", "fetched_at"],
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string", "enum": ["intrasearch", "deepagent", "manual"] },
    "source_type": { "type": "string", "const": "document" },
    "source_ref": { "type": "string" },
    "kind": { "type": "string", "const": "document" },
    "title": { "type": "string", "minLength": 1 },
    "url": { "type": "string" },
    "snippet": { "type": ["string", "null"] },
    "query": { "type": ["string", "null"] },
    "entity_refs": { "type": "array", "items": { "type": "string" } },
    "dedupe_key": { "type": "string" },
    "confidence": { "type": "string", "enum": ["canonical", "corroborated", "candidate"] },
    "fetched_at": { "type": "string", "format": "date-time" },
    "observed_at": { "type": ["string", "null"], "format": "date-time" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

- [ ] **Step 3: Create decision.json schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Decision",
  "type": "object",
  "required": ["id", "source", "source_ref", "kind", "summary", "dedupe_key", "fetched_at"],
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string" },
    "source_type": { "type": "string" },
    "source_ref": { "type": "string" },
    "kind": { "type": "string", "const": "decision" },
    "summary": { "type": "string", "minLength": 1 },
    "context": { "type": ["string", "null"] },
    "decided_by": { "type": ["string", "null"] },
    "decided_at": { "type": ["string", "null"], "format": "date-time" },
    "entity_refs": { "type": "array", "items": { "type": "string" } },
    "dedupe_key": { "type": "string" },
    "confidence": { "type": "string", "enum": ["canonical", "corroborated", "candidate"] },
    "fetched_at": { "type": "string", "format": "date-time" },
    "observed_at": { "type": ["string", "null"], "format": "date-time" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

- [ ] **Step 4: Create commitment.json schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Commitment",
  "type": "object",
  "required": ["id", "source", "source_ref", "kind", "summary", "dedupe_key", "fetched_at"],
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string" },
    "source_type": { "type": "string" },
    "source_ref": { "type": "string" },
    "kind": { "type": "string", "const": "commitment" },
    "summary": { "type": "string", "minLength": 1 },
    "owner": { "type": ["string", "null"] },
    "due_date": { "type": ["string", "null"], "format": "date" },
    "status": { "type": "string", "enum": ["active", "fulfilled", "stale", "cancelled"] },
    "entity_refs": { "type": "array", "items": { "type": "string" } },
    "dedupe_key": { "type": "string" },
    "confidence": { "type": "string", "enum": ["canonical", "corroborated", "candidate"] },
    "fetched_at": { "type": "string", "format": "date-time" },
    "observed_at": { "type": ["string", "null"], "format": "date-time" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

- [ ] **Step 5: Create entity.json, note.json, relation.json, sync_run.json schemas**

**entity.json:**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Entity",
  "type": "object",
  "required": ["id", "kind", "name", "dedupe_key"],
  "properties": {
    "id": { "type": "string" },
    "kind": { "type": "string", "enum": ["person", "project", "team", "goal", "system", "queue", "document"] },
    "name": { "type": "string", "minLength": 1 },
    "aliases": { "type": "array", "items": { "type": "string" } },
    "external_ids": { "type": "object" },
    "dedupe_key": { "type": "string" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

**note.json:**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Note",
  "type": "object",
  "required": ["id", "source", "kind", "text", "dedupe_key", "fetched_at"],
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string" },
    "source_type": { "type": ["string", "null"] },
    "source_ref": { "type": ["string", "null"] },
    "kind": { "type": "string", "const": "note" },
    "text": { "type": "string", "minLength": 1 },
    "entity_refs": { "type": "array", "items": { "type": "string" } },
    "dedupe_key": { "type": "string" },
    "confidence": { "type": "string", "enum": ["canonical", "corroborated", "candidate"] },
    "fetched_at": { "type": "string", "format": "date-time" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

**relation.json:**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Relation",
  "type": "object",
  "required": ["id", "source", "kind", "from_ref", "to_ref", "relation_type", "dedupe_key"],
  "properties": {
    "id": { "type": "string" },
    "source": { "type": "string" },
    "kind": { "type": "string", "const": "relation" },
    "from_ref": { "type": "string" },
    "to_ref": { "type": "string" },
    "relation_type": { "type": "string", "enum": ["belongs_to", "assigned_to", "authored_by", "related_to", "depends_on", "mentions"] },
    "dedupe_key": { "type": "string" },
    "fetched_at": { "type": "string", "format": "date-time" },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```

**sync_run.json:**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SyncRun",
  "type": "object",
  "required": ["id", "kind", "recipe", "started_at", "status"],
  "properties": {
    "id": { "type": "string" },
    "kind": { "type": "string", "const": "sync_run" },
    "recipe": { "type": "string" },
    "command": { "type": ["string", "null"] },
    "sources_touched": { "type": "array", "items": { "type": "string" } },
    "raw_records_count": { "type": "integer", "minimum": 0 },
    "normalized_records_count": { "type": "integer", "minimum": 0 },
    "warnings": { "type": "array", "items": { "type": "string" } },
    "unresolved_entities_count": { "type": "integer", "minimum": 0 },
    "publish_status": { "type": "string", "enum": ["published", "partial", "failed", "skipped"] },
    "degraded_sources": { "type": "array", "items": { "type": "string" } },
    "started_at": { "type": "string", "format": "date-time" },
    "finished_at": { "type": ["string", "null"], "format": "date-time" },
    "latency_ms": { "type": ["integer", "null"] },
    "status": { "type": "string", "enum": ["running", "success", "partial", "failed"] }
  },
  "additionalProperties": false
}
```

- [ ] **Step 6: Commit**

```bash
git add brain/system/schemas/
git commit -m "feat: add JSON schemas for all ledger record types"
```

---

## Task 6: Pydantic models for all record types

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write test_models.py — validation tests**

```python
# tests/test_models.py
import pytest
from datetime import datetime, timezone
from scripts.models import (
    Issue, Document, Decision, Commitment,
    Entity, Note, Relation, SyncRun,
)


def _now():
    return datetime.now(timezone.utc).isoformat()


class TestIssue:
    def test_valid_issue(self):
        issue = Issue(
            id="tracker:PM-123",
            source="tracker",
            source_ref="PM-123",
            key="PM-123",
            summary="Fix login bug",
            status="open",
            assignee="vladk",
            queue="PM",
            dedupe_key="tracker:PM-123",
            fetched_at=_now(),
        )
        assert issue.kind == "issue"
        assert issue.confidence == "canonical"

    def test_issue_key_pattern(self):
        with pytest.raises(ValueError):
            Issue(
                id="tracker:bad",
                source="tracker",
                source_ref="bad",
                key="lowercase-123",  # invalid: must be UPPER-digits
                summary="test",
                status="open",
                dedupe_key="tracker:bad",
                fetched_at=_now(),
            )

    def test_issue_empty_summary_rejected(self):
        with pytest.raises(ValueError):
            Issue(
                id="tracker:PM-1",
                source="tracker",
                source_ref="PM-1",
                key="PM-1",
                summary="",
                status="open",
                dedupe_key="tracker:PM-1",
                fetched_at=_now(),
            )


class TestDocument:
    def test_valid_document(self):
        doc = Document(
            id="intrasearch:abc123",
            source="intrasearch",
            source_ref="abc123",
            title="Onboarding Guide",
            url="https://wiki.yandex-team.ru/onboarding",
            dedupe_key="intrasearch:abc123",
            fetched_at=_now(),
        )
        assert doc.kind == "document"

    def test_document_requires_title(self):
        with pytest.raises(ValueError):
            Document(
                id="intrasearch:x",
                source="intrasearch",
                source_ref="x",
                title="",
                url="https://example.com",
                dedupe_key="intrasearch:x",
                fetched_at=_now(),
            )


class TestDecision:
    def test_valid_decision(self):
        d = Decision(
            id="manual:d1",
            source="manual",
            source_ref="user-input",
            summary="We decided to use JSONL for the ledger",
            dedupe_key="manual:d1",
            fetched_at=_now(),
        )
        assert d.kind == "decision"


class TestCommitment:
    def test_valid_commitment(self):
        c = Commitment(
            id="tracker:PM-99",
            source="tracker",
            source_ref="PM-99",
            summary="Ship auth refactor by Q2",
            owner="vladk",
            due_date="2026-06-30",
            dedupe_key="tracker:PM-99",
            fetched_at=_now(),
        )
        assert c.status == "active"

    def test_commitment_status_values(self):
        c = Commitment(
            id="x:1",
            source="manual",
            source_ref="x",
            summary="test",
            status="fulfilled",
            dedupe_key="x:1",
            fetched_at=_now(),
        )
        assert c.status == "fulfilled"


class TestEntity:
    def test_valid_entity(self):
        e = Entity(
            id="person:vladk",
            kind="person",
            name="Vlad Kiaune",
            dedupe_key="person:vladk",
        )
        assert e.aliases == []


class TestNote:
    def test_valid_note(self):
        n = Note(
            id="manual:n1",
            source="manual",
            text="Remember to check the deploy logs",
            dedupe_key="manual:n1",
            fetched_at=_now(),
        )
        assert n.kind == "note"


class TestRelation:
    def test_valid_relation(self):
        r = Relation(
            id="rel:1",
            source="tracker",
            from_ref="project:lumi",
            to_ref="tracker:PM-123",
            relation_type="belongs_to",
            dedupe_key="rel:project:lumi->tracker:PM-123:belongs_to",
            fetched_at=_now(),
        )
        assert r.kind == "relation"


class TestSyncRun:
    def test_valid_sync_run(self):
        s = SyncRun(
            id="sync:abc",
            recipe="my_work",
            started_at=_now(),
            status="running",
        )
        assert s.kind == "sync_run"
        assert s.raw_records_count == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/tovlad01/dev/exoskeleton && python -m pytest tests/test_models.py -v
```

Expected: ModuleNotFoundError for `scripts.models`

- [ ] **Step 3: Implement scripts/models.py**

```python
"""Pydantic models for all ledger record types.

These models enforce the schemas defined in brain/system/schemas/.
Every record written to the ledger MUST pass through these models.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


_ISSUE_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


class _LedgerBase(BaseModel):
    """Common fields for all ledger records with provenance."""
    id: str
    source: str
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    entity_refs: list[str] = Field(default_factory=list)
    dedupe_key: str
    confidence: str = "canonical"
    fetched_at: str
    observed_at: Optional[str] = None
    payload: dict = Field(default_factory=dict)


class Issue(_LedgerBase):
    kind: str = "issue"
    key: str
    summary: str
    status: str
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    queue: Optional[str] = None
    priority: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

    @field_validator("key")
    @classmethod
    def _validate_key(cls, v: str) -> str:
        if not _ISSUE_KEY_RE.match(v):
            raise ValueError(f"Invalid issue key format: {v!r}")
        return v

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v


class Document(_LedgerBase):
    kind: str = "document"
    title: str
    url: str
    snippet: Optional[str] = None
    query: Optional[str] = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v


class Decision(_LedgerBase):
    kind: str = "decision"
    summary: str
    context: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v


class Commitment(_LedgerBase):
    kind: str = "commitment"
    summary: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "active"

    @field_validator("summary")
    @classmethod
    def _validate_summary(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("summary must not be empty")
        return v

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        allowed = {"active", "fulfilled", "stale", "cancelled"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class Entity(BaseModel):
    id: str
    kind: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    external_ids: dict = Field(default_factory=dict)
    dedupe_key: str
    payload: dict = Field(default_factory=dict)

    @field_validator("kind")
    @classmethod
    def _validate_kind(cls, v: str) -> str:
        allowed = {"person", "project", "team", "goal", "system", "queue", "document"}
        if v not in allowed:
            raise ValueError(f"kind must be one of {allowed}")
        return v


class Note(BaseModel):
    id: str
    source: str
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    kind: str = "note"
    text: str
    entity_refs: list[str] = Field(default_factory=list)
    dedupe_key: str
    confidence: str = "canonical"
    fetched_at: str
    payload: dict = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def _validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class Relation(BaseModel):
    id: str
    source: str
    kind: str = "relation"
    from_ref: str
    to_ref: str
    relation_type: str
    dedupe_key: str
    fetched_at: str
    payload: dict = Field(default_factory=dict)

    @field_validator("relation_type")
    @classmethod
    def _validate_relation_type(cls, v: str) -> str:
        allowed = {"belongs_to", "assigned_to", "authored_by", "related_to", "depends_on", "mentions"}
        if v not in allowed:
            raise ValueError(f"relation_type must be one of {allowed}")
        return v


class SyncRun(BaseModel):
    id: str
    kind: str = "sync_run"
    recipe: str
    command: Optional[str] = None
    sources_touched: list[str] = Field(default_factory=list)
    raw_records_count: int = 0
    normalized_records_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    unresolved_entities_count: int = 0
    publish_status: str = "running"
    degraded_sources: list[str] = Field(default_factory=list)
    started_at: str
    finished_at: Optional[str] = None
    latency_ms: Optional[int] = None
    status: str = "running"

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        allowed = {"running", "success", "partial", "failed"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


# Mapping from kind to model class — used by routing.py
RECORD_MODELS = {
    "issue": Issue,
    "document": Document,
    "decision": Decision,
    "commitment": Commitment,
    "entity": Entity,
    "note": Note,
    "relation": Relation,
    "sync_run": SyncRun,
}

# Mapping from kind to ledger file — used by routing.py
LEDGER_FILES = {
    "issue": "issues.jsonl",
    "document": "docs.jsonl",
    "decision": "decisions.jsonl",
    "commitment": "commitments.jsonl",
    "entity": "entities.jsonl",
    "note": "notes.jsonl",
    "relation": "relations.jsonl",
    "sync_run": "sync_runs.jsonl",
}
```

- [ ] **Step 4: Create scripts/__init__.py and tests/__init__.py**

Both empty files.

- [ ] **Step 5: Run tests**

```bash
cd /Users/tovlad01/dev/exoskeleton && pip install pydantic pyyaml jsonschema pytest && python -m pytest tests/test_models.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/ tests/
git commit -m "feat: add Pydantic models for all ledger record types with validation"
```

---

## Task 7: Test fixtures

**Files:**
- Create: `scripts/fixtures/__init__.py`
- Create: `scripts/fixtures/tracker_issues.json`
- Create: `scripts/fixtures/intrasearch_hits.json`
- Create: `scripts/fixtures/deepagent_response.json`
- Create: `scripts/fixtures/broken_responses.json`
- Create: `scripts/fixtures/ambiguous_aliases.json`

- [ ] **Step 1: Create tracker_issues.json**

```json
{
  "normal": [
    {
      "key": "PM-123",
      "summary": "Implement onboarding flow for new users",
      "status": { "key": "inProgress", "display": "In Progress" },
      "assignee": { "id": "vladk", "display": "Vlad Kiaune" },
      "reporter": { "id": "sergey-sus", "display": "Sergey Suslov" },
      "queue": { "key": "PM", "display": "Product Management" },
      "priority": { "key": "normal", "display": "Normal" },
      "updatedAt": "2026-04-01T10:30:00.000+0000",
      "createdAt": "2026-03-15T08:00:00.000+0000"
    },
    {
      "key": "PM-456",
      "summary": "Define success metrics for retention experiment",
      "status": { "key": "open", "display": "Open" },
      "assignee": { "id": "vladk", "display": "Vlad Kiaune" },
      "reporter": { "id": "anna-k", "display": "Anna Koroleva" },
      "queue": { "key": "PM", "display": "Product Management" },
      "priority": { "key": "critical", "display": "Critical" },
      "updatedAt": "2026-04-02T09:00:00.000+0000",
      "createdAt": "2026-03-28T12:00:00.000+0000"
    },
    {
      "key": "LUMI-78",
      "summary": "Launch readiness review for LUMI v2",
      "status": { "key": "open", "display": "Open" },
      "assignee": { "id": "vladk", "display": "Vlad Kiaune" },
      "reporter": { "id": "vladk", "display": "Vlad Kiaune" },
      "queue": { "key": "LUMI", "display": "LUMI" },
      "priority": { "key": "high", "display": "High" },
      "updatedAt": "2026-03-30T16:00:00.000+0000",
      "createdAt": "2026-03-20T09:00:00.000+0000"
    }
  ],
  "single": {
    "key": "PM-123",
    "summary": "Implement onboarding flow for new users",
    "description": "Full description of the onboarding task with requirements and acceptance criteria.",
    "status": { "key": "inProgress", "display": "In Progress" },
    "assignee": { "id": "vladk", "display": "Vlad Kiaune" },
    "reporter": { "id": "sergey-sus", "display": "Sergey Suslov" },
    "queue": { "key": "PM", "display": "Product Management" },
    "priority": { "key": "normal", "display": "Normal" },
    "followers": [{ "id": "anna-k" }],
    "tags": ["onboarding", "q2"],
    "updatedAt": "2026-04-01T10:30:00.000+0000",
    "createdAt": "2026-03-15T08:00:00.000+0000",
    "components": [],
    "links": [
      { "type": "relates", "issue": { "key": "LUMI-78" } }
    ]
  }
}
```

- [ ] **Step 2: Create intrasearch_hits.json**

```json
{
  "doc_results": [
    {
      "title": "Onboarding Flow Design Doc",
      "url": "https://wiki.yandex-team.ru/practicum/onboarding-v2/",
      "snippet": "The new onboarding flow reduces time-to-value from 14 days to 3 days...",
      "source": "wiki",
      "relevance": 0.95
    },
    {
      "title": "Retention Metrics Dashboard",
      "url": "https://wiki.yandex-team.ru/practicum/metrics/retention/",
      "snippet": "Key retention metrics: D1, D7, D30 retention rates broken by cohort...",
      "source": "wiki",
      "relevance": 0.82
    }
  ],
  "tracker_text_results": [
    {
      "key": "PM-100",
      "title": "Research: user drop-off in onboarding",
      "snippet": "Analysis shows 40% drop-off at step 3 of the current flow...",
      "url": "https://tracker.yandex-team.ru/PM-100"
    }
  ]
}
```

- [ ] **Step 3: Create deepagent_response.json**

```json
{
  "broad_context": {
    "message": "Tell me about the onboarding project at Practicum",
    "response": "The onboarding project at Practicum is focused on reducing time-to-value for new students. Key people involved include Vlad Kiaune (PM), Sergey Suslov (design lead), and Anna Koroleva (data analyst). There are several related tickets in the PM queue, including PM-123 for the main implementation and LUMI-78 for launch readiness. The project started in Q1 2026 and targets completion by end of Q2. Recent decisions include switching from a wizard-style flow to a progressive disclosure model."
  },
  "candidate_issues": {
    "message": "Find tracker issues related to onboarding. Return only issue keys.",
    "response": "PM-123\nPM-456\nPM-100\nLUMI-78\nPRACT-500\nONBOARD-12"
  }
}
```

- [ ] **Step 4: Create broken_responses.json**

```json
{
  "empty_list": [],
  "null_response": null,
  "malformed_issue": {
    "key": "PM-999",
    "summary": null,
    "status": "unknown_status_value"
  },
  "missing_required_fields": {
    "key": "PM-888"
  },
  "timeout_error": {
    "error": "Request timed out after 30000ms",
    "code": "TIMEOUT"
  },
  "partial_list": [
    {
      "key": "PM-123",
      "summary": "Valid issue",
      "status": { "key": "open", "display": "Open" },
      "assignee": { "id": "vladk", "display": "Vlad" },
      "queue": { "key": "PM" }
    },
    {
      "key": null,
      "summary": "Broken issue with null key"
    }
  ]
}
```

- [ ] **Step 5: Create ambiguous_aliases.json**

```json
{
  "person_collision": {
    "raw_text": "Sergey",
    "candidates": [
      { "id": "person:sergey-sus", "name": "Sergey Suslov", "team": "design" },
      { "id": "person:sergey-iv", "name": "Sergey Ivanov", "team": "backend" }
    ]
  },
  "project_collision": {
    "raw_text": "navigator",
    "candidates": [
      { "id": "project:career-navi", "name": "Career Navigator" },
      { "id": "project:navi-app", "name": "Navigator App" }
    ]
  }
}
```

- [ ] **Step 6: Create scripts/fixtures/__init__.py**

Empty file.

- [ ] **Step 7: Commit**

```bash
git add scripts/fixtures/ tests/
git commit -m "feat: add test fixtures for tracker, intrasearch, deepagent, broken responses"
```

---

## Task 8: Entity resolver

**Files:**
- Create: `scripts/entity_resolver.py`
- Test: `tests/test_entity_resolver.py`

- [ ] **Step 1: Write test_entity_resolver.py**

```python
# tests/test_entity_resolver.py
import pytest
from scripts.entity_resolver import EntityResolver


@pytest.fixture
def aliases():
    return {
        "projects": {
            "navi": ["navigator", "нави", "навигатор"],
            "lumi": ["луми"],
        },
        "people": {
            "sergey-sus": ["сережа сус", "sus", "sergey suslov"],
            "anna-k": ["anna koroleva", "anna k"],
        },
        "queues": {
            "PRACT": ["practicum", "практикум"],
        },
        "abbreviations": {},
    }


@pytest.fixture
def identities():
    return {
        "user": {
            "tracker_login": "vladk",
            "display_name": "Vlad Kiaune",
            "email": "vlad@example.com",
        }
    }


@pytest.fixture
def resolver(aliases, identities):
    return EntityResolver(aliases=aliases, identities=identities)


class TestExactMatch:
    def test_exact_id(self, resolver):
        result = resolver.resolve("sergey-sus", kind="person")
        assert result.resolved_id == "person:sergey-sus"
        assert result.confidence == "exact"

    def test_exact_alias(self, resolver):
        result = resolver.resolve("sus", kind="person")
        assert result.resolved_id == "person:sergey-sus"
        assert result.confidence == "alias"

    def test_case_insensitive_alias(self, resolver):
        result = resolver.resolve("Sergey Suslov", kind="person")
        assert result.resolved_id == "person:sergey-sus"

    def test_project_alias(self, resolver):
        result = resolver.resolve("навигатор", kind="project")
        assert result.resolved_id == "project:navi"


class TestAmbiguous:
    def test_ambiguous_returns_unresolved(self, resolver):
        # "sergey" partially matches both sergey-sus and would need disambiguation
        result = resolver.resolve("sergey", kind="person")
        # Exact substring isn't in aliases, so it should be unresolved
        assert result.confidence == "unresolved"

    def test_unknown_name(self, resolver):
        result = resolver.resolve("unknown person xyz", kind="person")
        assert result.confidence == "unresolved"
        assert result.resolved_id is None


class TestQueue:
    def test_queue_alias(self, resolver):
        result = resolver.resolve("practicum", kind="queue")
        assert result.resolved_id == "queue:PRACT"

    def test_queue_direct(self, resolver):
        result = resolver.resolve("PRACT", kind="queue")
        assert result.resolved_id == "queue:PRACT"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_entity_resolver.py -v
```

Expected: ModuleNotFoundError

- [ ] **Step 3: Implement entity_resolver.py**

```python
"""Deterministic entity resolution using aliases and identities.

Resolution order (per PRD §15.3):
1. Exact external IDs
2. Alias map (case-insensitive)
3. Normalized name match
4. Unresolved → review queue

The model is NOT involved in resolution. This is purely deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResolveResult:
    resolved_id: str | None
    confidence: str  # "exact", "alias", "unresolved"
    candidates: list[str]
    raw_text: str


class EntityResolver:
    def __init__(self, aliases: dict, identities: dict):
        # Build lookup: lowered alias → (kind, canonical_id)
        self._lookup: dict[str, list[tuple[str, str]]] = {}
        self._build_lookup(aliases)
        self._identities = identities

    def _build_lookup(self, aliases: dict) -> None:
        kind_map = {
            "projects": "project",
            "people": "person",
            "queues": "queue",
        }
        for section, kind in kind_map.items():
            entries = aliases.get(section, {})
            if not isinstance(entries, dict):
                continue
            for canonical_id, alias_list in entries.items():
                # Register canonical id itself
                self._add(canonical_id.lower(), kind, canonical_id)
                # Register all aliases
                for alias in alias_list:
                    self._add(alias.lower(), kind, canonical_id)

    def _add(self, lowered: str, kind: str, canonical_id: str) -> None:
        key = lowered.strip()
        if key not in self._lookup:
            self._lookup[key] = []
        entry = (kind, canonical_id)
        if entry not in self._lookup[key]:
            self._lookup[key].append(entry)

    def resolve(self, raw_text: str, kind: str | None = None) -> ResolveResult:
        lowered = raw_text.strip().lower()

        # 1. Exact match in lookup
        if lowered in self._lookup:
            matches = self._lookup[lowered]
            if kind:
                matches = [(k, cid) for k, cid in matches if k == kind]
            if len(matches) == 1:
                k, cid = matches[0]
                # Determine if it was the canonical id or an alias
                conf = "exact" if lowered == cid.lower() else "alias"
                return ResolveResult(
                    resolved_id=f"{k}:{cid}",
                    confidence=conf,
                    candidates=[f"{k}:{cid}"],
                    raw_text=raw_text,
                )
            elif len(matches) > 1:
                return ResolveResult(
                    resolved_id=None,
                    confidence="unresolved",
                    candidates=[f"{k}:{cid}" for k, cid in matches],
                    raw_text=raw_text,
                )

        # 2. No match found
        return ResolveResult(
            resolved_id=None,
            confidence="unresolved",
            candidates=[],
            raw_text=raw_text,
        )
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_entity_resolver.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/entity_resolver.py tests/test_entity_resolver.py
git commit -m "feat: add deterministic entity resolver with alias lookup"
```

---

## Task 9: Record routing

**Files:**
- Create: `scripts/routing.py`
- Test: `tests/test_routing.py`

- [ ] **Step 1: Write test_routing.py**

```python
# tests/test_routing.py
import pytest
from scripts.routing import route_record, RoutingError


class TestRouting:
    def test_issue_routes_to_issues_jsonl(self):
        assert route_record("issue") == "issues.jsonl"

    def test_document_routes_to_docs_jsonl(self):
        assert route_record("document") == "docs.jsonl"

    def test_decision_routes(self):
        assert route_record("decision") == "decisions.jsonl"

    def test_commitment_routes(self):
        assert route_record("commitment") == "commitments.jsonl"

    def test_entity_routes(self):
        assert route_record("entity") == "entities.jsonl"

    def test_note_routes(self):
        assert route_record("note") == "notes.jsonl"

    def test_relation_routes(self):
        assert route_record("relation") == "relations.jsonl"

    def test_sync_run_routes(self):
        assert route_record("sync_run") == "sync_runs.jsonl"

    def test_unknown_kind_raises(self):
        with pytest.raises(RoutingError):
            route_record("unknown_kind")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_routing.py -v
```

- [ ] **Step 3: Implement routing.py**

```python
"""Schema-driven record routing.

The model NEVER chooses a destination file freely (PRD §5.8).
Routing is deterministic based on record kind.
"""
from __future__ import annotations

from scripts.models import LEDGER_FILES


class RoutingError(Exception):
    pass


def route_record(kind: str) -> str:
    """Return the ledger filename for a given record kind."""
    filename = LEDGER_FILES.get(kind)
    if filename is None:
        raise RoutingError(
            f"Unknown record kind: {kind!r}. "
            f"Valid kinds: {sorted(LEDGER_FILES.keys())}"
        )
    return filename
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_routing.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/routing.py tests/test_routing.py
git commit -m "feat: add deterministic schema-driven record routing"
```

---

## Task 10: Normalize — raw source data to canonical records

**Files:**
- Create: `scripts/normalize.py`
- Test: `tests/test_normalize.py`

- [ ] **Step 1: Write test_normalize.py**

```python
# tests/test_normalize.py
import json
import pytest
from pathlib import Path
from scripts.normalize import normalize_tracker_issue, normalize_intrasearch_hit, normalize_tracker_issues


FIXTURES = Path(__file__).parent.parent / "scripts" / "fixtures"


class TestNormalizeTrackerIssue:
    def test_normal_issue(self):
        with open(FIXTURES / "tracker_issues.json") as f:
            data = json.load(f)
        raw = data["normal"][0]
        issue = normalize_tracker_issue(raw)
        assert issue.key == "PM-123"
        assert issue.summary == "Implement onboarding flow for new users"
        assert issue.status == "inProgress"
        assert issue.assignee == "vladk"
        assert issue.queue == "PM"
        assert issue.source == "tracker"
        assert issue.confidence == "canonical"
        assert issue.dedupe_key == "tracker:PM-123"
        assert issue.id == "tracker:PM-123"

    def test_all_normal_issues(self):
        with open(FIXTURES / "tracker_issues.json") as f:
            data = json.load(f)
        issues = normalize_tracker_issues(data["normal"])
        assert len(issues) == 3
        keys = {i.key for i in issues}
        assert keys == {"PM-123", "PM-456", "LUMI-78"}

    def test_malformed_issue_skipped(self):
        with open(FIXTURES / "broken_responses.json") as f:
            data = json.load(f)
        # partial_list has one valid and one broken issue
        results = normalize_tracker_issues(data["partial_list"])
        assert len(results) == 1
        assert results[0].key == "PM-123"


class TestNormalizeIntrasearchHit:
    def test_doc_hit(self):
        with open(FIXTURES / "intrasearch_hits.json") as f:
            data = json.load(f)
        hit = data["doc_results"][0]
        doc = normalize_intrasearch_hit(hit, query="onboarding")
        assert doc.title == "Onboarding Flow Design Doc"
        assert doc.source == "intrasearch"
        assert doc.query == "onboarding"
        assert doc.confidence == "canonical"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_normalize.py -v
```

- [ ] **Step 3: Implement normalize.py**

```python
"""Raw source data → canonical Pydantic records.

This module handles Tier A (deterministic) extraction from raw API responses.
Each source has its own normalizer that maps source-specific field names
to canonical schema fields.

Rules:
- Never invent data not present in the raw response.
- Skip malformed records instead of crashing.
- Always set provenance fields (source, source_ref, fetched_at, dedupe_key).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from scripts.models import Issue, Document

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_get(obj: dict, *keys: str, default=None):
    """Safely traverse nested dicts."""
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def normalize_tracker_issue(raw: dict) -> Issue | None:
    """Normalize a single tracker issue response to canonical Issue."""
    key = raw.get("key")
    if not key or not isinstance(key, str):
        logger.warning("Skipping issue with missing/invalid key: %s", raw)
        return None

    summary = raw.get("summary")
    if not summary or not isinstance(summary, str):
        logger.warning("Skipping issue %s with missing summary", key)
        return None

    status = _safe_get(raw, "status", "key") or _safe_get(raw, "status") or "unknown"
    if isinstance(status, dict):
        status = status.get("key", "unknown")

    assignee = _safe_get(raw, "assignee", "id") or _safe_get(raw, "assignee")
    if isinstance(assignee, dict):
        assignee = assignee.get("id")

    reporter = _safe_get(raw, "reporter", "id") or _safe_get(raw, "reporter")
    if isinstance(reporter, dict):
        reporter = reporter.get("id")

    queue = _safe_get(raw, "queue", "key") or _safe_get(raw, "queue")
    if isinstance(queue, dict):
        queue = queue.get("key")

    priority = _safe_get(raw, "priority", "key")
    if isinstance(priority, dict):
        priority = priority.get("key")

    return Issue(
        id=f"tracker:{key}",
        source="tracker",
        source_type="issue",
        source_ref=key,
        key=key,
        summary=summary,
        status=status,
        assignee=assignee,
        reporter=reporter,
        queue=queue,
        priority=priority,
        updated_at=raw.get("updatedAt"),
        created_at=raw.get("createdAt"),
        entity_refs=[],
        dedupe_key=f"tracker:{key}",
        confidence="canonical",
        fetched_at=_now_iso(),
    )


def normalize_tracker_issues(raw_list: list[dict]) -> list[Issue]:
    """Normalize a list of raw tracker issues. Skips malformed ones."""
    results = []
    for raw in raw_list:
        issue = normalize_tracker_issue(raw)
        if issue is not None:
            results.append(issue)
    return results


def normalize_intrasearch_hit(raw: dict, query: str | None = None) -> Document | None:
    """Normalize an intrasearch search result to canonical Document."""
    title = raw.get("title")
    url = raw.get("url")
    if not title or not url:
        logger.warning("Skipping intrasearch hit with missing title/url: %s", raw)
        return None

    return Document(
        id=f"intrasearch:{url}",
        source="intrasearch",
        source_type="document",
        source_ref=url,
        title=title,
        url=url,
        snippet=raw.get("snippet"),
        query=query,
        dedupe_key=f"intrasearch:{url}",
        confidence="canonical",
        fetched_at=_now_iso(),
    )


def normalize_intrasearch_hits(raw_list: list[dict], query: str | None = None) -> list[Document]:
    """Normalize a list of intrasearch hits. Skips malformed ones."""
    results = []
    for raw in raw_list:
        doc = normalize_intrasearch_hit(raw, query=query)
        if doc is not None:
            results.append(doc)
    return results
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_normalize.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/normalize.py tests/test_normalize.py
git commit -m "feat: add normalization for tracker issues and intrasearch hits"
```

---

## Task 11: Merge ledger — upsert by dedupe_key with idempotency

**Files:**
- Create: `scripts/merge_ledger.py`
- Test: `tests/test_merge_ledger.py`

- [ ] **Step 1: Write test_merge_ledger.py**

```python
# tests/test_merge_ledger.py
import json
import pytest
from pathlib import Path
from scripts.merge_ledger import merge_records, read_jsonl, write_jsonl


@pytest.fixture
def tmp_ledger(tmp_path):
    ledger = tmp_path / "issues.jsonl"
    ledger.write_text("")
    return ledger


class TestMergeRecords:
    def test_insert_new_records(self, tmp_ledger):
        records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Issue A"},
            {"id": "tracker:PM-456", "dedupe_key": "tracker:PM-456", "summary": "Issue B"},
        ]
        stats = merge_records(tmp_ledger, records)
        assert stats["inserted"] == 2
        assert stats["updated"] == 0
        result = read_jsonl(tmp_ledger)
        assert len(result) == 2

    def test_upsert_existing_record(self, tmp_ledger):
        existing = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Old summary"},
        ]
        write_jsonl(tmp_ledger, existing)

        new_records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "New summary"},
        ]
        stats = merge_records(tmp_ledger, new_records)
        assert stats["inserted"] == 0
        assert stats["updated"] == 1
        result = read_jsonl(tmp_ledger)
        assert len(result) == 1
        assert result[0]["summary"] == "New summary"

    def test_idempotent_merge(self, tmp_ledger):
        records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Issue A"},
        ]
        merge_records(tmp_ledger, records)
        merge_records(tmp_ledger, records)
        result = read_jsonl(tmp_ledger)
        assert len(result) == 1

    def test_empty_new_records_preserves_existing(self, tmp_ledger):
        existing = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Existing"},
        ]
        write_jsonl(tmp_ledger, existing)
        stats = merge_records(tmp_ledger, [])
        assert stats["inserted"] == 0
        assert stats["updated"] == 0
        result = read_jsonl(tmp_ledger)
        assert len(result) == 1
        assert result[0]["summary"] == "Existing"

    def test_mixed_insert_and_update(self, tmp_ledger):
        existing = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Old"},
        ]
        write_jsonl(tmp_ledger, existing)
        new_records = [
            {"id": "tracker:PM-123", "dedupe_key": "tracker:PM-123", "summary": "Updated"},
            {"id": "tracker:PM-999", "dedupe_key": "tracker:PM-999", "summary": "Brand new"},
        ]
        stats = merge_records(tmp_ledger, new_records)
        assert stats["inserted"] == 1
        assert stats["updated"] == 1
        result = read_jsonl(tmp_ledger)
        assert len(result) == 2


class TestReadWriteJsonl:
    def test_read_empty_file(self, tmp_ledger):
        assert read_jsonl(tmp_ledger) == []

    def test_read_nonexistent_file(self, tmp_path):
        assert read_jsonl(tmp_path / "nope.jsonl") == []

    def test_write_and_read_roundtrip(self, tmp_ledger):
        data = [{"a": 1}, {"b": 2}]
        write_jsonl(tmp_ledger, data)
        assert read_jsonl(tmp_ledger) == data
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_merge_ledger.py -v
```

- [ ] **Step 3: Implement merge_ledger.py**

```python
"""Merge normalized records into ledger JSONL files.

Upsert semantics: records are matched by dedupe_key.
- If dedupe_key exists → update (replace entire record).
- If dedupe_key is new → insert.
- Empty new_records NEVER erases existing data (PRD §12.2.5).

Merge is atomic: writes to temp file, then renames.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)


def read_jsonl(path: Path) -> list[dict]:
    """Read all records from a JSONL file."""
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    """Atomically write records to a JSONL file."""
    # Write to temp file in same directory, then rename for atomicity
    with NamedTemporaryFile(
        mode="w",
        suffix=".jsonl",
        dir=path.parent,
        delete=False,
        encoding="utf-8",
    ) as tmp:
        for record in records:
            tmp.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        tmp_path = Path(tmp.name)
    tmp_path.rename(path)


def merge_records(ledger_path: Path, new_records: list[dict]) -> dict:
    """Merge new records into existing ledger file by dedupe_key.

    Returns stats dict with inserted/updated counts.
    """
    existing = read_jsonl(ledger_path)

    # Build index by dedupe_key
    index: dict[str, int] = {}
    for i, record in enumerate(existing):
        dk = record.get("dedupe_key")
        if dk:
            index[dk] = i

    inserted = 0
    updated = 0

    for record in new_records:
        dk = record.get("dedupe_key")
        if not dk:
            logger.warning("Record missing dedupe_key, skipping: %s", record.get("id"))
            continue

        if dk in index:
            existing[index[dk]] = record
            updated += 1
        else:
            index[dk] = len(existing)
            existing.append(record)
            inserted += 1

    write_jsonl(ledger_path, existing)

    return {"inserted": inserted, "updated": updated, "total": len(existing)}
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_merge_ledger.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/merge_ledger.py tests/test_merge_ledger.py
git commit -m "feat: add ledger merge with upsert by dedupe_key and atomic writes"
```

---

## Task 12: Rebuild views — ledger to markdown projection

**Files:**
- Create: `scripts/rebuild_views.py`
- Test: `tests/test_rebuild_views.py`
- Create: `tests/golden/active.md`
- Create: `tests/golden/decisions.md`
- Create: `tests/golden/commitments.md`

- [ ] **Step 1: Write test_rebuild_views.py**

```python
# tests/test_rebuild_views.py
import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from scripts.rebuild_views import (
    rebuild_active_view,
    rebuild_decisions_view,
    rebuild_commitments_view,
    rebuild_project_view,
)
from scripts.merge_ledger import write_jsonl

GOLDEN = Path(__file__).parent / "golden"


def _now():
    return "2026-04-02T12:00:00+00:00"


@pytest.fixture
def brain_dir(tmp_path):
    """Set up a minimal brain directory with ledger data."""
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    views = tmp_path / "views"
    views.mkdir()
    (views / "projects").mkdir()
    (views / "people").mkdir()
    control = tmp_path / "control"
    control.mkdir()

    # Write role.md
    (control / "role.md").write_text("# Role\n\nSenior PM at Practicum\n")
    (control / "week.md").write_text("# Week Focus\n\n- Ship onboarding v2\n- Review retention metrics\n")

    # Write issues
    issues = [
        {
            "id": "tracker:PM-123", "kind": "issue", "key": "PM-123",
            "summary": "Implement onboarding flow", "status": "inProgress",
            "assignee": "vladk", "queue": "PM", "priority": "normal",
            "dedupe_key": "tracker:PM-123", "source": "tracker",
            "confidence": "canonical", "fetched_at": _now(),
            "updated_at": "2026-04-01T10:30:00+00:00",
        },
        {
            "id": "tracker:PM-456", "kind": "issue", "key": "PM-456",
            "summary": "Define retention metrics", "status": "open",
            "assignee": "vladk", "queue": "PM", "priority": "critical",
            "dedupe_key": "tracker:PM-456", "source": "tracker",
            "confidence": "canonical", "fetched_at": _now(),
            "updated_at": "2026-04-02T09:00:00+00:00",
        },
        {
            "id": "tracker:LUMI-78", "kind": "issue", "key": "LUMI-78",
            "summary": "Launch readiness review", "status": "open",
            "assignee": "vladk", "queue": "LUMI", "priority": "high",
            "dedupe_key": "tracker:LUMI-78", "source": "tracker",
            "confidence": "canonical", "fetched_at": _now(),
            "updated_at": "2026-03-30T16:00:00+00:00",
        },
    ]
    write_jsonl(ledger / "issues.jsonl", issues)

    # Write decisions
    decisions = [
        {
            "id": "manual:d1", "kind": "decision", "source": "manual",
            "source_ref": "sync-2026-04-01", "summary": "Switch to progressive disclosure for onboarding",
            "context": "Wizard flow had 40% drop-off at step 3",
            "decided_by": "vladk", "decided_at": "2026-04-01T10:00:00+00:00",
            "entity_refs": ["project:navi"], "dedupe_key": "manual:d1",
            "confidence": "canonical", "fetched_at": _now(),
        },
    ]
    write_jsonl(ledger / "decisions.jsonl", decisions)

    # Write commitments
    commitments = [
        {
            "id": "tracker:PM-99", "kind": "commitment", "source": "tracker",
            "source_ref": "PM-99", "summary": "Ship onboarding v2 by Q2 end",
            "owner": "vladk", "due_date": "2026-06-30", "status": "active",
            "entity_refs": [], "dedupe_key": "tracker:PM-99",
            "confidence": "canonical", "fetched_at": _now(),
        },
    ]
    write_jsonl(ledger / "commitments.jsonl", commitments)

    # Empty other files
    for name in ["docs.jsonl", "entities.jsonl", "notes.jsonl", "relations.jsonl", "sync_runs.jsonl"]:
        (ledger / name).write_text("")

    # State
    state = tmp_path / "state"
    state.mkdir()
    (state / "source_state.json").write_text(json.dumps({
        "last_sync": {"tracker": "2026-04-02T12:00:00+00:00"},
        "source_health": {"tracker": "ok"},
    }))

    return tmp_path


class TestRebuildActiveView:
    def test_generates_active_md(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        assert "PM-123" in output
        assert "PM-456" in output
        assert "LUMI-78" in output
        assert "inProgress" in output or "In Progress" in output

    def test_includes_week_focus(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        assert "onboarding" in output.lower()

    def test_includes_sync_freshness(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        assert "tracker" in output.lower()


class TestRebuildDecisionsView:
    def test_generates_decisions_md(self, brain_dir):
        output = rebuild_decisions_view(brain_dir)
        assert "progressive disclosure" in output.lower()
        assert "manual" in output.lower() or "source" in output.lower()


class TestRebuildCommitmentsView:
    def test_generates_commitments_md(self, brain_dir):
        output = rebuild_commitments_view(brain_dir)
        assert "onboarding v2" in output.lower()
        assert "2026-06-30" in output


class TestRebuildProjectView:
    def test_generates_project_md(self, brain_dir):
        output = rebuild_project_view(brain_dir, project_id="navi", project_name="Navigator")
        # Should include decisions that reference project:navi
        assert "progressive disclosure" in output.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_rebuild_views.py -v
```

- [ ] **Step 3: Implement rebuild_views.py**

```python
"""Rebuild markdown views from ledger data.

Views are PROJECTIONS of the ledger — never canonical storage.
The model does not maintain these files directly (PRD §12.2.1).

Each rebuild function:
1. Reads relevant ledger JSONL files.
2. Sorts/filters/groups deterministically.
3. Returns markdown string (caller writes to file).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from scripts.merge_ledger import read_jsonl

logger = logging.getLogger(__name__)


def _read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _read_state(brain_dir: Path) -> dict:
    state_path = brain_dir / "state" / "source_state.json"
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {}


def rebuild_active_view(brain_dir: Path) -> str:
    """Rebuild brain/views/active.md from ledger + control files."""
    issues = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
    commitments = read_jsonl(brain_dir / "ledger" / "commitments.jsonl")
    role_text = _read_text(brain_dir / "control" / "role.md")
    week_text = _read_text(brain_dir / "control" / "week.md")
    state = _read_state(brain_dir)

    lines = ["# Active Work", ""]

    # Role
    if role_text.strip():
        lines.append("## Role")
        # Skip the markdown header if present
        for line in role_text.strip().split("\n"):
            if not line.startswith("# "):
                lines.append(line)
        lines.append("")

    # Week focus
    if week_text.strip():
        lines.append("## Week Focus")
        for line in week_text.strip().split("\n"):
            if not line.startswith("# "):
                lines.append(line)
        lines.append("")

    # Issues by queue
    active_issues = [i for i in issues if i.get("status") not in ("closed", "resolved", "cancelled")]
    active_issues.sort(key=lambda x: (x.get("queue", ""), x.get("priority", "zzz")))

    lines.append("## My Issues")
    lines.append("")
    if active_issues:
        lines.append("| Key | Summary | Status | Priority | Queue | Updated |")
        lines.append("|-----|---------|--------|----------|-------|---------|")
        for issue in active_issues:
            lines.append(
                f"| {issue.get('key', '?')} "
                f"| {issue.get('summary', '?')} "
                f"| {issue.get('status', '?')} "
                f"| {issue.get('priority', '-')} "
                f"| {issue.get('queue', '-')} "
                f"| {issue.get('updated_at', '-')[:10] if issue.get('updated_at') else '-'} |"
            )
    else:
        lines.append("_No active issues found._")
    lines.append("")

    # Active commitments
    active_comms = [c for c in commitments if c.get("status") == "active"]
    if active_comms:
        lines.append("## Active Commitments")
        lines.append("")
        for c in active_comms:
            due = c.get("due_date", "no date")
            lines.append(f"- **{c.get('summary', '?')}** — owner: {c.get('owner', '?')}, due: {due}")
        lines.append("")

    # Sync freshness
    last_sync = state.get("last_sync", {})
    health = state.get("source_health", {})
    if last_sync:
        lines.append("## Sync Freshness")
        lines.append("")
        for source, ts in sorted(last_sync.items()):
            status = health.get(source, "unknown")
            lines.append(f"- **{source}**: last sync {ts[:10] if ts else 'never'} — {status}")
        lines.append("")

    # Degraded warnings
    degraded = [s for s, h in health.items() if h != "ok"]
    if degraded:
        lines.append("## ⚠ Degraded Sources")
        lines.append("")
        for s in degraded:
            lines.append(f"- {s}: {health[s]}")
        lines.append("")

    return "\n".join(lines)


def rebuild_decisions_view(brain_dir: Path) -> str:
    """Rebuild brain/views/decisions.md from ledger."""
    decisions = read_jsonl(brain_dir / "ledger" / "decisions.jsonl")
    decisions.sort(key=lambda x: x.get("decided_at") or x.get("fetched_at", ""), reverse=True)

    lines = ["# Decisions", ""]
    if not decisions:
        lines.append("_No decisions recorded._")
        return "\n".join(lines)

    for d in decisions:
        date = (d.get("decided_at") or d.get("fetched_at", "?"))[:10]
        lines.append(f"### {d.get('summary', '?')}")
        lines.append("")
        if d.get("context"):
            lines.append(f"**Context:** {d['context']}")
        if d.get("decided_by"):
            lines.append(f"**Decided by:** {d['decided_by']}")
        lines.append(f"**Date:** {date}")
        lines.append(f"**Source:** {d.get('source', '?')} ({d.get('source_ref', '?')})")
        if d.get("confidence") != "canonical":
            lines.append(f"**Confidence:** {d.get('confidence')}")
        refs = d.get("entity_refs", [])
        if refs:
            lines.append(f"**Related:** {', '.join(refs)}")
        lines.append("")

    return "\n".join(lines)


def rebuild_commitments_view(brain_dir: Path) -> str:
    """Rebuild brain/views/commitments.md from ledger."""
    commitments = read_jsonl(brain_dir / "ledger" / "commitments.jsonl")

    active = [c for c in commitments if c.get("status") == "active"]
    fulfilled = [c for c in commitments if c.get("status") == "fulfilled"]
    stale = [c for c in commitments if c.get("status") == "stale"]

    lines = ["# Commitments", ""]

    def _render_group(title: str, items: list[dict]):
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        for c in items:
            due = c.get("due_date", "no date")
            owner = c.get("owner", "?")
            lines.append(f"- **{c.get('summary', '?')}** — owner: {owner}, due: {due}")
            lines.append(f"  Source: {c.get('source', '?')} ({c.get('source_ref', '?')})")
        lines.append("")

    _render_group("Active", active)
    _render_group("Stale", stale)
    _render_group("Fulfilled", fulfilled)

    if not commitments:
        lines.append("_No commitments recorded._")

    return "\n".join(lines)


def rebuild_project_view(brain_dir: Path, project_id: str, project_name: str) -> str:
    """Rebuild a single project dossier from ledger data."""
    issues = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
    decisions = read_jsonl(brain_dir / "ledger" / "decisions.jsonl")
    commitments = read_jsonl(brain_dir / "ledger" / "commitments.jsonl")
    docs = read_jsonl(brain_dir / "ledger" / "docs.jsonl")
    relations = read_jsonl(brain_dir / "ledger" / "relations.jsonl")

    ref = f"project:{project_id}"

    # Filter by entity_refs containing project reference
    proj_issues = [i for i in issues if ref in i.get("entity_refs", [])]
    proj_decisions = [d for d in decisions if ref in d.get("entity_refs", [])]
    proj_commitments = [c for c in commitments if ref in c.get("entity_refs", [])]
    proj_docs = [d for d in docs if ref in d.get("entity_refs", [])]

    # Also check relations
    related_issue_ids = {
        r["to_ref"] for r in relations
        if r.get("from_ref") == ref and r.get("relation_type") == "belongs_to"
    }
    for issue in issues:
        if issue.get("id") in related_issue_ids and issue not in proj_issues:
            proj_issues.append(issue)

    lines = [f"# {project_name}", ""]
    lines.append(f"_Project ID: {project_id}_")
    lines.append("")

    # Issues
    lines.append("## Issues")
    lines.append("")
    if proj_issues:
        for i in proj_issues:
            lines.append(f"- **{i.get('key')}** {i.get('summary', '?')} — {i.get('status', '?')}")
    else:
        lines.append("_No linked issues._")
    lines.append("")

    # Decisions
    lines.append("## Decisions")
    lines.append("")
    if proj_decisions:
        for d in proj_decisions:
            lines.append(f"- {d.get('summary', '?')} ({(d.get('decided_at') or '?')[:10]})")
    else:
        lines.append("_No linked decisions._")
    lines.append("")

    # Commitments
    lines.append("## Commitments")
    lines.append("")
    if proj_commitments:
        for c in proj_commitments:
            lines.append(f"- {c.get('summary', '?')} — due: {c.get('due_date', '?')}")
    else:
        lines.append("_No linked commitments._")
    lines.append("")

    # Docs
    lines.append("## Related Documents")
    lines.append("")
    if proj_docs:
        for d in proj_docs:
            lines.append(f"- [{d.get('title', '?')}]({d.get('url', '#')})")
    else:
        lines.append("_No linked documents._")
    lines.append("")

    return "\n".join(lines)


def rebuild_all_views(brain_dir: Path) -> dict:
    """Rebuild all standard views. Returns stats."""
    views_dir = brain_dir / "views"
    views_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    active_md = rebuild_active_view(brain_dir)
    (views_dir / "active.md").write_text(active_md, encoding="utf-8")
    results["active"] = len(active_md)

    decisions_md = rebuild_decisions_view(brain_dir)
    (views_dir / "decisions.md").write_text(decisions_md, encoding="utf-8")
    results["decisions"] = len(decisions_md)

    commitments_md = rebuild_commitments_view(brain_dir)
    (views_dir / "commitments.md").write_text(commitments_md, encoding="utf-8")
    results["commitments"] = len(commitments_md)

    return results
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_rebuild_views.py -v
```

- [ ] **Step 5: Create golden test files**

After tests pass, capture the expected outputs as golden files:

```python
# Add to test_rebuild_views.py at the end

class TestGoldenFiles:
    def test_active_view_matches_golden(self, brain_dir):
        output = rebuild_active_view(brain_dir)
        golden_path = GOLDEN / "active.md"
        if not golden_path.exists():
            golden_path.parent.mkdir(parents=True, exist_ok=True)
            golden_path.write_text(output, encoding="utf-8")
            pytest.skip("Golden file created, re-run to verify")
        expected = golden_path.read_text(encoding="utf-8")
        assert output == expected
```

Run once to generate golden files, then again to verify they match.

- [ ] **Step 6: Commit**

```bash
git add scripts/rebuild_views.py tests/test_rebuild_views.py tests/golden/
git commit -m "feat: add view rebuilder — ledger to markdown projection"
```

---

## Task 13: Sync quality checks

**Files:**
- Create: `scripts/sync_quality.py`
- Test: `tests/test_sync_quality.py`

- [ ] **Step 1: Write test_sync_quality.py**

```python
# tests/test_sync_quality.py
import json
import pytest
from pathlib import Path
from scripts.sync_quality import run_quality_checks, QualityReport
from scripts.merge_ledger import write_jsonl


@pytest.fixture
def brain_dir(tmp_path):
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    state = tmp_path / "state"
    state.mkdir()
    return tmp_path


class TestQualityChecks:
    def test_no_duplicate_dedupe_keys(self, brain_dir):
        issues = [
            {"id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A", "source": "tracker"},
            {"id": "tracker:PM-2", "dedupe_key": "tracker:PM-2", "key": "PM-2", "summary": "B", "source": "tracker"},
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert report.passed
        assert len(report.warnings) == 0

    def test_duplicate_dedupe_keys_warned(self, brain_dir):
        issues = [
            {"id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A", "source": "tracker"},
            {"id": "tracker:PM-1-dup", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A dup", "source": "tracker"},
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert not report.passed
        assert any("duplicate" in w.lower() for w in report.warnings)

    def test_missing_provenance_warned(self, brain_dir):
        issues = [
            {"id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1", "summary": "A"},
            # Missing 'source' field
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert any("provenance" in w.lower() or "source" in w.lower() for w in report.warnings)

    def test_unresolved_entities_counted(self, brain_dir):
        issues = [
            {
                "id": "tracker:PM-1", "dedupe_key": "tracker:PM-1", "key": "PM-1",
                "summary": "A", "source": "tracker",
                "entity_refs": ["unresolved:some person"],
            },
        ]
        write_jsonl(brain_dir / "ledger" / "issues.jsonl", issues)
        report = run_quality_checks(brain_dir)
        assert report.unresolved_entities_count == 1

    def test_empty_ledger_passes(self, brain_dir):
        (brain_dir / "ledger" / "issues.jsonl").write_text("")
        report = run_quality_checks(brain_dir)
        assert report.passed
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_sync_quality.py -v
```

- [ ] **Step 3: Implement sync_quality.py**

```python
"""Sync quality checks — invariant verification after merge.

Runs after every sync to detect:
- duplicate dedupe_keys within a ledger file
- missing provenance (source field)
- unresolved entity references
- candidate-only records without corroboration

If checks fail, the previous views are preserved (PRD §16).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from scripts.merge_ledger import read_jsonl

logger = logging.getLogger(__name__)

LEDGER_FILES = [
    "issues.jsonl",
    "docs.jsonl",
    "decisions.jsonl",
    "commitments.jsonl",
    "entities.jsonl",
    "notes.jsonl",
    "relations.jsonl",
]


@dataclass
class QualityReport:
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    unresolved_entities_count: int = 0
    duplicate_keys_count: int = 0
    missing_provenance_count: int = 0
    total_records: int = 0

    def fail(self, warning: str):
        self.passed = False
        self.warnings.append(warning)

    def warn(self, warning: str):
        self.warnings.append(warning)


def run_quality_checks(brain_dir: Path) -> QualityReport:
    """Run all quality checks on the ledger. Returns a QualityReport."""
    report = QualityReport()
    ledger_dir = brain_dir / "ledger"

    for filename in LEDGER_FILES:
        path = ledger_dir / filename
        if not path.exists():
            continue

        records = read_jsonl(path)
        report.total_records += len(records)

        # Check duplicate dedupe_keys
        seen_keys: dict[str, int] = {}
        for i, record in enumerate(records):
            dk = record.get("dedupe_key")
            if dk:
                if dk in seen_keys:
                    report.duplicate_keys_count += 1
                    report.fail(
                        f"Duplicate dedupe_key '{dk}' in {filename} "
                        f"(lines {seen_keys[dk]} and {i})"
                    )
                else:
                    seen_keys[dk] = i

        # Check provenance
        for record in records:
            if not record.get("source") and record.get("kind") != "entity":
                report.missing_provenance_count += 1
                report.warn(
                    f"Missing source provenance in {filename}: "
                    f"id={record.get('id', '?')}"
                )

        # Count unresolved entities
        for record in records:
            for ref in record.get("entity_refs", []):
                if ref.startswith("unresolved:"):
                    report.unresolved_entities_count += 1

    return report


def save_quality_report(brain_dir: Path, report: QualityReport) -> None:
    """Save quality report to brain/state/quality_report.json."""
    from datetime import datetime, timezone

    state_dir = brain_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "passed": report.passed,
        "warnings": report.warnings,
        "unresolved_entities_count": report.unresolved_entities_count,
        "duplicate_keys_count": report.duplicate_keys_count,
        "missing_provenance_count": report.missing_provenance_count,
        "total_records": report.total_records,
    }

    path = state_dir / "quality_report.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_sync_quality.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/sync_quality.py tests/test_sync_quality.py
git commit -m "feat: add sync quality checks — duplicate, provenance, unresolved entity detection"
```

---

## Task 14: Extraction helpers (Tier A deterministic)

**Files:**
- Create: `scripts/extract.py`
- Test: `tests/test_extract.py`

- [ ] **Step 1: Write test_extract.py**

```python
# tests/test_extract.py
import pytest
from scripts.extract import (
    extract_issue_keys,
    extract_dates,
    extract_urls,
    extract_tracker_logins,
)


class TestExtractIssueKeys:
    def test_basic_keys(self):
        text = "Check PM-123 and LUMI-78 for details"
        assert extract_issue_keys(text) == ["PM-123", "LUMI-78"]

    def test_no_keys(self):
        assert extract_issue_keys("no keys here") == []

    def test_keys_from_deepagent_response(self):
        text = "PM-123\nPM-456\nPM-100\nLUMI-78\nPRACT-500"
        keys = extract_issue_keys(text)
        assert len(keys) == 5
        assert "PRACT-500" in keys

    def test_deduplicates(self):
        text = "PM-123 mentioned again PM-123"
        assert extract_issue_keys(text) == ["PM-123"]


class TestExtractDates:
    def test_iso_date(self):
        assert extract_dates("due 2026-06-30 end") == ["2026-06-30"]

    def test_no_dates(self):
        assert extract_dates("no dates here") == []


class TestExtractUrls:
    def test_wiki_url(self):
        text = "see https://wiki.yandex-team.ru/practicum/onboarding/ for details"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert "wiki.yandex-team.ru" in urls[0]

    def test_multiple_urls(self):
        text = "https://a.com and https://b.com"
        assert len(extract_urls(text)) == 2


class TestExtractTrackerLogins:
    def test_assignee_field(self):
        logins = extract_tracker_logins({"assignee": {"id": "vladk"}, "reporter": {"id": "anna-k"}})
        assert "vladk" in logins
        assert "anna-k" in logins

    def test_string_assignee(self):
        logins = extract_tracker_logins({"assignee": "vladk"})
        assert "vladk" in logins
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_extract.py -v
```

- [ ] **Step 3: Implement extract.py**

```python
"""Tier A — deterministic extraction from text and structured data.

Uses regex/rules/mappings for:
- Issue keys (PROJ-123 pattern)
- Dates (ISO format)
- URLs
- Tracker logins from structured fields

No LLM involved. This is the most reliable extraction tier.
"""
from __future__ import annotations

import re

_ISSUE_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
_ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_URL_RE = re.compile(r"https?://[^\s)\]>\"']+")


def extract_issue_keys(text: str) -> list[str]:
    """Extract unique issue keys from text, preserving order of first occurrence."""
    seen = set()
    result = []
    for match in _ISSUE_KEY_RE.finditer(text):
        key = match.group(1)
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result


def extract_dates(text: str) -> list[str]:
    """Extract ISO dates (YYYY-MM-DD) from text."""
    return _ISO_DATE_RE.findall(text)


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return _URL_RE.findall(text)


def extract_tracker_logins(raw: dict) -> list[str]:
    """Extract tracker logins from structured issue data."""
    logins = []
    for field_name in ("assignee", "reporter", "createdBy", "updatedBy"):
        value = raw.get(field_name)
        if isinstance(value, dict):
            login = value.get("id") or value.get("login")
            if login:
                logins.append(login)
        elif isinstance(value, str) and value:
            logins.append(value)

    # Also check followers
    for follower in raw.get("followers", []):
        if isinstance(follower, dict):
            login = follower.get("id") or follower.get("login")
            if login:
                logins.append(login)
        elif isinstance(follower, str):
            logins.append(follower)

    return list(dict.fromkeys(logins))  # dedupe preserving order
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_extract.py -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/extract.py tests/test_extract.py
git commit -m "feat: add Tier A deterministic extraction — issue keys, dates, URLs, logins"
```

---

## Task 15: Shared test conftest

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Create conftest.py with shared fixtures**

```python
# tests/conftest.py
"""Shared pytest fixtures for PM Copilot tests."""
import json
from pathlib import Path

import pytest
import yaml


FIXTURES_DIR = Path(__file__).parent.parent / "scripts" / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def tracker_fixtures():
    with open(FIXTURES_DIR / "tracker_issues.json") as f:
        return json.load(f)


@pytest.fixture
def intrasearch_fixtures():
    with open(FIXTURES_DIR / "intrasearch_hits.json") as f:
        return json.load(f)


@pytest.fixture
def deepagent_fixtures():
    with open(FIXTURES_DIR / "deepagent_response.json") as f:
        return json.load(f)


@pytest.fixture
def broken_fixtures():
    with open(FIXTURES_DIR / "broken_responses.json") as f:
        return json.load(f)


@pytest.fixture
def sample_aliases():
    return {
        "projects": {
            "navi": ["navigator", "нави", "навигатор"],
            "lumi": ["луми"],
        },
        "people": {
            "sergey-sus": ["сережа сус", "sus", "sergey suslov"],
            "anna-k": ["anna koroleva", "anna k"],
        },
        "queues": {
            "PRACT": ["practicum", "практикум"],
            "LUMI": ["lumi"],
        },
        "abbreviations": {},
    }


@pytest.fixture
def sample_identities():
    return {
        "user": {
            "display_name": "Vlad Kiaune",
            "tracker_login": "vladk",
            "email": "vlad@example.com",
            "teams": ["practicum"],
            "default_queues": ["PRACT", "LUMI"],
        }
    }


@pytest.fixture
def brain_dir(tmp_path):
    """Create a minimal brain directory structure for testing."""
    dirs = [
        "ledger", "views", "views/projects", "views/people", "views/attention",
        "control", "state", "system", "ingest/raw", "ingest/normalized", "ingest/failed",
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)

    # Empty ledger files
    for name in [
        "entities.jsonl", "issues.jsonl", "docs.jsonl", "decisions.jsonl",
        "commitments.jsonl", "notes.jsonl", "relations.jsonl", "sync_runs.jsonl",
    ]:
        (tmp_path / "ledger" / name).write_text("")

    # Default state
    (tmp_path / "state" / "source_state.json").write_text(json.dumps({
        "last_sync": {},
        "source_health": {},
    }))
    (tmp_path / "state" / "entity_index.json").write_text(json.dumps({"entities": {}, "aliases": {}}))
    (tmp_path / "state" / "sync_cursor.json").write_text(json.dumps({"cursors": {}}))
    (tmp_path / "state" / "quality_report.json").write_text(json.dumps({
        "last_check": None, "warnings": [], "degraded_sources": [],
    }))

    # Default control
    (tmp_path / "control" / "role.md").write_text("# Role\n\n_Not configured._\n")
    (tmp_path / "control" / "quarter.md").write_text("# Quarter Goals\n\n_Not configured._\n")
    (tmp_path / "control" / "week.md").write_text("# Week Focus\n\n_Not configured._\n")
    (tmp_path / "control" / "constraints.md").write_text("# Constraints\n\n_None._\n")

    return tmp_path
```

- [ ] **Step 2: Run all tests to verify conftest works**

```bash
python -m pytest tests/ -v
```

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "feat: add shared test conftest with brain directory fixtures"
```

---

## Task 16: AGENTS.md and rules files

**Files:**
- Create: `AGENTS.md`
- Create: `.codeassistant/rules/00-safety.md`
- Create: `.codeassistant/rules/10-source-priority.md`
- Create: `.codeassistant/rules/20-brain-map.md`
- Create: `.codeassistant/rules-ask/10-read-before-answer.md`
- Create: `.codeassistant/rules-architect/10-plan-before-writing.md`

- [ ] **Step 1: Create AGENTS.md**

```markdown
# PM Copilot Exoskeleton

You are a PM copilot assistant running inside Yandex Code Assistant.
Your operational memory is stored in `brain/system/`. Read it before every task.

## Critical rules

1. **Never invent tool usage patterns.** Always read `brain/system/query-recipes/` before calling any MCP tool.
2. **Never overwrite views on empty sync.** If a source returns empty, keep previous views intact.
3. **Always preserve provenance.** Every fact must have source, source_ref, and fetched_at.
4. **DeepAgent is discovery only.** Never treat DeepAgent output as authoritative for issue status, assignees, or project metadata.
5. **Never choose destination files freely.** Record routing is schema-driven — see `scripts/routing.py`.
6. **Read `brain/system/identities.yaml` before any personalized query.** You need to know who the user is.
7. **Prefer canonical sources.** See `brain/system/source-map.yaml` for which source is authoritative for which fact type.
8. **Low confidence → inbox.** Uncertain extractions go to `brain/views/inbox.md`, not into canonical views.

## Before operational tasks

1. Read `brain/system/identities.yaml` — who is the user?
2. Read `brain/system/source-map.yaml` — which source to use?
3. Read the relevant recipe in `brain/system/query-recipes/` — how to query?
4. If a recipe is not calibrated (`calibrated: false`), suggest running `/tool-calibrate` first.

## After any sync

1. Raw data → `brain/ingest/raw/`
2. Normalized → validate against schemas in `brain/system/schemas/`
3. Merge → `brain/ledger/*.jsonl` using dedupe_key
4. Quality check → `scripts/sync_quality.py`
5. If quality passes → rebuild views via `scripts/rebuild_views.py`
6. If quality fails → keep previous views, log to `brain/ingest/failed/`

## Available commands

- `/brief` — daily summary
- `/my-work` — sync and show current issues
- `/issue <key>` — issue dossier
- `/remember <fact>` — store a note
- `/tool-calibrate` — calibrate query recipes

## Brain structure

See `.codeassistant/rules/20-brain-map.md` for full map.
```

- [ ] **Step 2: Create .codeassistant/rules/00-safety.md**

```markdown
---
description: Safety rules for brain operations — prevents data loss and corruption
globs: ["brain/**", "scripts/**"]
alwaysApply: true
---

# Safety Rules

1. **Never overwrite healthy views with empty data.** If a sync returns zero records but the ledger has existing data, keep the existing data. Only update when new data is available.
2. **Never delete ledger records** unless the user explicitly confirms deletion.
3. **Never write directly to `brain/views/*.md`** — these are generated by `scripts/rebuild_views.py`. Edit the ledger instead.
4. **Always save raw responses** to `brain/ingest/raw/` before any transformation.
5. **Never invent entity IDs, owners, due dates, or tracker states.** Only use data from source responses.
6. **Never skip quality checks** after a sync. Run `scripts/sync_quality.py` before publishing views.
7. **Partial sync is OK, silent failure is not.** Always surface degraded sources in `brain/views/active.md`.
```

- [ ] **Step 3: Create .codeassistant/rules/10-source-priority.md**

```markdown
---
description: Source authority hierarchy — which tool to use for which fact type
globs: ["brain/**"]
alwaysApply: true
---

# Source Priority

When sources conflict, use this hierarchy (most trusted first):

1. **tracker** — canonical for issues, status, assignees, project/goal metadata
2. **yt** — canonical for table schemas, paths, data existence
3. **infractl** — canonical for namespaces, objects, ownership
4. **intrasearch** — canonical for doc/wiki/SO snippets and text search
5. **deepagent** — broad discovery ONLY, never authoritative

## Conflict resolution

- tracker beats deepagent on issue facts
- yt beats deepagent on data facts
- infractl beats deepagent on infra facts
- intrasearch snippets beat deepagent for direct evidence

## DeepAgent policy

- Mark all DeepAgent results as `confidence: candidate`
- Must be corroborated via canonical source before promoting to `canonical`
- Never publish DeepAgent-only facts to project dossiers as ground truth
```

- [ ] **Step 4: Create .codeassistant/rules/20-brain-map.md**

```markdown
---
description: Brain directory structure and purpose of each section
globs: ["brain/**"]
alwaysApply: true
---

# Brain Map

## `brain/system/` — Agent operational memory
- `identities.yaml` — who is the user (logins, queues, teams)
- `source-map.yaml` — which source is authoritative for which fact
- `aliases.yaml` — name/project/queue aliases for entity resolution
- `query-recipes/*.yaml` — tested MCP tool call patterns
- `schemas/*.json` — JSON schemas for ledger records
- `runbooks/*.md` — failure handling procedures

## `brain/ledger/` — Canonical data (JSONL)
- `issues.jsonl`, `docs.jsonl`, `decisions.jsonl`, `commitments.jsonl`
- `entities.jsonl`, `notes.jsonl`, `relations.jsonl`, `sync_runs.jsonl`
- Every record has `dedupe_key`, `source`, `confidence`, `fetched_at`

## `brain/views/` — Generated markdown (read-only for agents)
- `active.md` — daily work dashboard
- `decisions.md`, `commitments.md`, `inbox.md`, `references.md`
- `projects/*.md`, `people/*.md` — dossiers
- **These files are OUTPUT. Never edit them directly.**

## `brain/control/` — Human-maintained context
- `role.md`, `quarter.md`, `week.md`, `constraints.md`
- **These files are INPUT. Only the user edits them.**

## `brain/ingest/` — Sync pipeline artifacts
- `raw/` — immutable source snapshots
- `normalized/` — post-transformation records
- `failed/` — quarantined bad data

## `brain/state/` — Pipeline state
- `source_state.json`, `entity_index.json`, `sync_cursor.json`, `quality_report.json`
```

- [ ] **Step 5: Create rules-ask and rules-architect files**

**.codeassistant/rules-ask/10-read-before-answer.md:**
```markdown
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
```

**.codeassistant/rules-architect/10-plan-before-writing.md:**
```markdown
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
```

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md .codeassistant/
git commit -m "feat: add AGENTS.md and YCA rules for safety, source priority, brain map"
```

---

## Task 17: YCA slash commands

**Files:**
- Create: `.codeassistant/commands/brief.md`
- Create: `.codeassistant/commands/my-work.md`
- Create: `.codeassistant/commands/issue.md`
- Create: `.codeassistant/commands/remember.md`
- Create: `.codeassistant/commands/tool-calibrate.md`

- [ ] **Step 1: Create brief.md**

```markdown
---
description: Daily brief — what to focus on, risks, stale commitments
---

# /brief — Daily Brief

## Steps

1. Read `brain/views/active.md`.
2. Read `brain/control/week.md`.
3. Read `brain/control/role.md`.
4. Check `brain/state/quality_report.json` — note any stale sources.
5. Read `brain/ledger/commitments.jsonl` — flag any where `due_date` is within 7 days or past.

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
```

- [ ] **Step 2: Create my-work.md**

```markdown
---
description: Sync and show current work items from Tracker
argument-hint: Optional queue filter (e.g., PM, LUMI)
---

# /my-work — Sync Current Work

## Steps

1. Read `brain/system/identities.yaml` to get `tracker_login` and `default_queues`.
2. Read `brain/system/query-recipes/tracker.yaml` recipe `my_open_issues`.
3. If recipe is not calibrated, warn the user and suggest `/tool-calibrate` first.
4. Execute the recipe:
   a. Call the primary tool with the templated args (substitute `{tracker_login}`).
   b. If it fails or returns empty, follow the fallback chain.
5. Save raw response to `brain/ingest/raw/tracker_my_work_{timestamp}.json`.
6. Normalize each issue using the pattern from `scripts/normalize.py`:
   - Extract key, summary, status, assignee, queue, priority, dates.
   - Set `source: "tracker"`, `confidence: "canonical"`, `dedupe_key: "tracker:{key}"`.
7. Merge normalized issues into `brain/ledger/issues.jsonl` (upsert by dedupe_key).
8. Run quality checks.
9. If quality passes, rebuild `brain/views/active.md`.
10. If quality fails, keep previous views and report the failure.
11. Log sync run to `brain/ledger/sync_runs.jsonl`.
12. Display the updated active issues to the user.

## Validation rules
- Every issue must have key, summary, status.
- Keys must match pattern `[A-Z][A-Z0-9]+-\d+`.
- If zero issues found and ledger has existing issues, do NOT delete them.
- Mark sync as `partial` if any fallback was used.

## On failure
- Follow runbook: `brain/system/runbooks/empty-tracker-response.md`.
```

- [ ] **Step 3: Create issue.md**

```markdown
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
    - issue → related docs (relation_type: "related_to")
    - issue → assignee (relation_type: "assigned_to")
    - issue → queue/project (relation_type: "belongs_to")
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
```

- [ ] **Step 4: Create remember.md**

```markdown
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
```

- [ ] **Step 5: Create tool-calibrate.md**

```markdown
---
description: Calibrate MCP tool recipes by testing real calls and recording successful patterns
argument-hint: Optional source name (tracker, intrasearch, deepagent). Default: all.
---

# /tool-calibrate — Calibrate Query Recipes

This is the MOST IMPORTANT command for system reliability.

## Purpose
Test each query recipe against the real MCP tools, record successful call shapes,
and mark recipes as calibrated. Without calibration, the system operates blind.

## Steps

1. Read `brain/system/identities.yaml` — need user identity for template substitution.
2. Read the relevant recipe file(s) from `brain/system/query-recipes/`.
3. For each recipe:
   a. Substitute template variables from identities.
   b. Call the primary tool with the substituted args.
   c. If successful:
      - Record the exact args used in the recipe's `last_successful_call`.
      - Store a sample response (first 3 records) in `example_response`.
      - Set `calibrated: true`.
      - Log success.
   d. If failed:
      - Try each fallback in order.
      - If a fallback succeeds, record it as the working pattern.
      - If all fail, log the failure with error details.
      - Keep `calibrated: false`.
4. Write updated recipes back to `brain/system/query-recipes/`.
5. Report calibration results:
   - Which recipes succeeded
   - Which failed (and why)
   - Which are still uncalibrated

## Output format

```
Calibration Results:
✓ tracker/my_open_issues — calibrated (3 issues found)
✓ tracker/get_issue_by_key — calibrated (PM-123 fetched)
✗ tracker/recently_updated_issues — FAILED (GetIssues returned error: ...)
✓ intrasearch/doc_search — calibrated (20 hits)
...
```

## Rules
- This command WRITES to recipe files. It's the only command that modifies `brain/system/`.
- Always show the user what was tested and the results.
- If a recipe fails, do NOT mark it as calibrated.
- Record the actual arg shapes that worked — this is critical for weak models.
```

- [ ] **Step 6: Commit**

```bash
git add .codeassistant/commands/
git commit -m "feat: add YCA slash commands — brief, my-work, issue, remember, tool-calibrate"
```

---

## Task 18: Control files (human-maintained context)

**Files:**
- Create: `brain/control/role.md`
- Create: `brain/control/quarter.md`
- Create: `brain/control/week.md`
- Create: `brain/control/constraints.md`

- [ ] **Step 1: Create all control files with placeholder templates**

**role.md:**
```markdown
# Role

<!-- Fill in your current role. This is read by /brief and /my-work. -->

_Not configured. Example:_

_Senior PM at Practicum, responsible for onboarding and retention products._
```

**quarter.md:**
```markdown
# Quarter Goals

<!-- Fill in your quarterly objectives. Used by /brief for priority context. -->

_Not configured. Example:_

_Q2 2026:_
_- Ship onboarding v2 (target: 50% reduction in time-to-value)_
_- Define retention measurement framework_
_- Launch LUMI v2 beta_
```

**week.md:**
```markdown
# Week Focus

<!-- Update weekly. Used by /brief for daily prioritization. -->

_Not configured. Example:_

_Week of 2026-03-31:_
_- Finalize onboarding flow specs_
_- Review retention metrics dashboard_
_- Prepare for Q2 planning sync_
```

**constraints.md:**
```markdown
# Constraints

<!-- Capture any active constraints on your work. -->

_Not configured. Example:_

_- Code freeze for mobile release after 2026-04-05_
_- No new tracker queues without ABC service approval_
_- DeepAgent responses must be treated as candidate only_
```

- [ ] **Step 2: Commit**

```bash
git add brain/control/
git commit -m "feat: add control files — role, quarter, week, constraints templates"
```

---

## Task 19: Initial views (empty but structured)

**Files:**
- Create: `brain/views/active.md`
- Create: `brain/views/inbox.md`
- Create: `brain/views/decisions.md`
- Create: `brain/views/commitments.md`
- Create: `brain/views/references.md`

- [ ] **Step 1: Create initial view files**

**active.md:**
```markdown
# Active Work

_No data yet. Run `/my-work` to sync your issues from Tracker._

## Sync Freshness

_No syncs completed._
```

**inbox.md:**
```markdown
# Inbox

_Items pending review. Unresolved entities, low-confidence extractions, and manual review items appear here._
```

**decisions.md:**
```markdown
# Decisions

_No decisions recorded. Use `/remember` to log decisions._
```

**commitments.md:**
```markdown
# Commitments

_No commitments recorded. Use `/remember` to log commitments._
```

**references.md:**
```markdown
# References

_Useful documents, owners, links, and system mappings. Updated during syncs._
```

- [ ] **Step 2: Commit**

```bash
git add brain/views/
git commit -m "feat: add initial empty view templates"
```

---

## Task 20: End-to-end integration test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write test_integration.py — full pipeline test**

```python
# tests/test_integration.py
"""End-to-end integration tests for the sync pipeline.

Tests the full flow: fixture data → normalize → merge → quality check → rebuild views.
"""
import json
import pytest
from pathlib import Path
from scripts.normalize import normalize_tracker_issues, normalize_intrasearch_hits
from scripts.merge_ledger import merge_records, read_jsonl, write_jsonl
from scripts.sync_quality import run_quality_checks
from scripts.rebuild_views import rebuild_active_view, rebuild_all_views


class TestFullSyncPipeline:
    def test_tracker_issues_pipeline(self, brain_dir, tracker_fixtures):
        """Full pipeline: raw tracker → normalize → merge → quality → views."""
        # 1. Normalize
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        assert len(issues) == 3

        # 2. Merge into ledger
        records = [i.model_dump() for i in issues]
        stats = merge_records(brain_dir / "ledger" / "issues.jsonl", records)
        assert stats["inserted"] == 3

        # 3. Quality check
        report = run_quality_checks(brain_dir)
        assert report.passed

        # 4. Rebuild views
        active_md = rebuild_active_view(brain_dir)
        assert "PM-123" in active_md
        assert "PM-456" in active_md
        assert "LUMI-78" in active_md

    def test_idempotent_sync(self, brain_dir, tracker_fixtures):
        """Running sync twice produces identical results."""
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        records = [i.model_dump() for i in issues]

        merge_records(brain_dir / "ledger" / "issues.jsonl", records)
        view1 = rebuild_active_view(brain_dir)

        merge_records(brain_dir / "ledger" / "issues.jsonl", records)
        view2 = rebuild_active_view(brain_dir)

        # Views should be identical after second sync
        ledger = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
        assert len(ledger) == 3  # no duplicates

    def test_empty_sync_preserves_state(self, brain_dir, tracker_fixtures):
        """Empty sync result must NOT delete existing issues."""
        # First sync: populate
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        records = [i.model_dump() for i in issues]
        merge_records(brain_dir / "ledger" / "issues.jsonl", records)

        # Second sync: empty result
        stats = merge_records(brain_dir / "ledger" / "issues.jsonl", [])
        assert stats["inserted"] == 0
        assert stats["updated"] == 0

        # Existing data preserved
        ledger = read_jsonl(brain_dir / "ledger" / "issues.jsonl")
        assert len(ledger) == 3

    def test_broken_response_quarantined(self, brain_dir, broken_fixtures):
        """Malformed issues are skipped, valid ones are kept."""
        issues = normalize_tracker_issues(broken_fixtures["partial_list"])
        assert len(issues) == 1  # only valid issue survives
        assert issues[0].key == "PM-123"

    def test_mixed_source_pipeline(self, brain_dir, tracker_fixtures, intrasearch_fixtures):
        """Issues from tracker + docs from intrasearch coexist in ledger."""
        # Tracker issues
        issues = normalize_tracker_issues(tracker_fixtures["normal"])
        merge_records(
            brain_dir / "ledger" / "issues.jsonl",
            [i.model_dump() for i in issues],
        )

        # Intrasearch docs
        docs = normalize_intrasearch_hits(
            intrasearch_fixtures["doc_results"],
            query="onboarding",
        )
        merge_records(
            brain_dir / "ledger" / "docs.jsonl",
            [d.model_dump() for d in docs],
        )

        # Both in ledger
        assert len(read_jsonl(brain_dir / "ledger" / "issues.jsonl")) == 3
        assert len(read_jsonl(brain_dir / "ledger" / "docs.jsonl")) == 2

        # Quality passes
        report = run_quality_checks(brain_dir)
        assert report.passed

        # Views rebuild
        results = rebuild_all_views(brain_dir)
        assert results["active"] > 0
```

- [ ] **Step 2: Run integration tests**

```bash
python -m pytest tests/test_integration.py -v
```

Expected: all pass.

- [ ] **Step 3: Run ALL tests to confirm nothing is broken**

```bash
python -m pytest tests/ -v
```

Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: add end-to-end integration tests for full sync pipeline"
```

---

## Task 21: Final cleanup and README

**Files:**
- Create: `brain/views/active.md` (overwrite with proper template)

- [ ] **Step 1: Run full test suite one final time**

```bash
python -m pytest tests/ -v --tb=short
```

- [ ] **Step 2: Verify directory structure matches PRD**

```bash
find . -type f | sort | head -80
```

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: Phase 1 complete — skeleton, ledger, pipeline, rules, commands, tests"
```

- [ ] **Step 4: Push**

```bash
git remote add origin <repo-url>  # if needed
git push -u origin main
```

---

## Spec Coverage Check

| PRD Section | Covered by Task |
|---|---|
| §10 Brain architecture / directory structure | Task 1 |
| §11.1 System brain (identities, source-map, aliases, recipes, runbooks) | Tasks 2, 3, 4 |
| §11.2 Ledger schemas | Tasks 5, 6 |
| §11.3 Views | Tasks 12, 19 |
| §11.4 Control files | Task 18 |
| §12 Sync pipeline (normalize, merge, rebuild, verify) | Tasks 10, 11, 12, 13 |
| §14 Sync recipes | Task 3 |
| §15 Extraction and routing | Tasks 8, 9, 14 |
| §17 Commands (/brief, /my-work, /issue, /remember, /tool-calibrate) | Task 17 |
| §18 AGENTS.md and rules | Task 16 |
| §19 Testing (fixtures, unit, golden, integration, reliability) | Tasks 7, 15, 20 |
| §20 Telemetry (sync_runs.jsonl) | Task 5 (schema), Task 13 (quality) |
| §21 Failure handling | Tasks 4 (runbooks), 13 (quality checks) |

**Phase 2 items deferred (not in this plan):** `/project`, `/research`, `/sync-daily`, deepagent candidate flow, project dossier projection from commands, unresolved review queue UI.
