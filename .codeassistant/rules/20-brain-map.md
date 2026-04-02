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
