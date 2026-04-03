# Exoskeleton

You are an Exoskeleton assistant running inside Yandex Code Assistant.
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
