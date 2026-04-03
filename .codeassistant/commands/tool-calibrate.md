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
   - If `tracker_login` is empty → run first-run auto-setup (see AGENTS.md), then continue.
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

## Rules
- This command WRITES to recipe files. It's the only command that modifies `brain/system/`.
- Always show the user what was tested and the results.
- If a recipe fails, do NOT mark it as calibrated.
- Record the actual arg shapes that worked — this is critical for weak models.
