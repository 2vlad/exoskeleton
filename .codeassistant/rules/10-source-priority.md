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
