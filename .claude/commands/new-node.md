---
description: Scaffold a new BFL FLUX model node — picks the right base class, builds INPUT_TYPES + generate_image, wires NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS, and updates the README node table. Drives the bfl-new-node skill.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(rg:*), Bash(grep:*)
argument-hint: <ClassName> [generation|finetune|utility] [model-endpoint-name]
---

# `/new-node` — scaffold a new BFL node

Adds a new ComfyUI node that wraps a BFL FLUX endpoint, following every convention in `CLAUDE.md` (`_BFL` registry key, ` (BFL)` display name, `BaseFlux` inheritance, conditional argument inclusion, graceful blank-image fallback).

This command **drives the `bfl-new-node` skill** — invoke it and follow its checklist.

## What you should know before running

- **ClassName** (Python identifier): bare, no `_BFL` suffix. Example: `Flux3`, `FluxKontextUltra`.
- **Kind**: `generation` (most common) → `BaseFlux`, category `"BFL"`. Or `finetune` → `BaseFinetuneFlux`, category `"BFL/Finetune"`. Or `utility` → no base class, category `"BFL/Utility"`.
- **Model endpoint name**: the path segment the BFL API expects, e.g. `flux-pro-1.1`, `flux-dev`, `flux-2-pro`. Used in `super().generate_image("<endpoint>", arguments, config)`.

If any of those is missing from `$ARGUMENTS`, the skill asks once at the top.

## Workflow

Invoke the `bfl-new-node` skill. It will:

1. Pick the right base class (`BaseFlux` / `BaseFinetuneFlux`) and category.
2. Decide where the new class goes (`nodes/api_node.py` for generation, `nodes/finetune.py` for finetune).
3. Write `INPUT_TYPES`: required block (`prompt`, dims OR `aspect_ratio`, model-specific params, `output_format`), optional block (`seed`, optional `image_prompt`, `webhook_url`, `webhook_secret`, `config: BFL_CONFIG`).
4. Write `generate_image(...)`: build `arguments` dict, conditional inclusion for `seed != -1` and non-empty optionals, call `super().generate_image("<endpoint>", arguments, config)`. Prefer `super().generate_image(...)` over inlining `post_request` + `get_result` — the base class runs dimension validation for you.
5. Register the class in the module's `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` with the `_BFL` / ` (BFL)` suffixes.
6. Add a row to the README node table under the right section (Generation / Finetune / Config / Utils).
7. Verify (see skill).

## What this command does NOT do

- Does NOT commit — user runs `/commit` after.
- Does NOT bump version — user runs `/version-bump` when releasing.
- Does NOT add a dependency.
- Does NOT touch `web/js/` — the new node renders with ComfyUI's default UI.
