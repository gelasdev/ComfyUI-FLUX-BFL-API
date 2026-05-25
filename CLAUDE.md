<!-- DO NOT REGENERATE via /init — manually maintained -->

# CLAUDE.md

> **Attribution.** The four behavioral rules below ("Think Before Coding", "Simplicity First", "Surgical Changes", "Goal-Driven Execution") are reproduced **verbatim** from Andrej Karpathy's [`CLAUDE.md`](https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md), distributed via the `forrestchang/andrej-karpathy-skills` repository (transferred to [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills) in May 2026). Used verbatim with attribution; no edits to wording. Project-specific rules follow under **`## BFL Project Rules`**.

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## BFL Project Rules

This is a **ComfyUI custom-nodes package** that wraps the **Black Forest Labs (BFL) FLUX** image-generation API. Single Python package, ~1000 LOC, no test framework, ruff for lint/format.

### Always do

- **Inheritance**: every new generation node inherits from `BaseFlux` (`nodes/base.py`). Every finetune node inherits from `BaseFinetuneFlux` (same file). The base class owns `post_request` / `get_result` / `process_result` / `create_blank_image` / `check_multiple_of_32` — do **not** reimplement those.
- **Node registration**:
  - Python class name is bare (e.g., `FluxPro11`, `FluxDev`). The one exception is `FluxConfig_BFL` where the class name matches its registry key for historical reasons.
  - ComfyUI **registry key** in `NODE_CLASS_MAPPINGS` ends with `_BFL`: `"FluxPro11_BFL": FluxPro11`.
  - ComfyUI **display name** in `NODE_DISPLAY_NAME_MAPPINGS` ends with ` (BFL)`: `"FluxPro11_BFL": "Flux Pro 1.1 (BFL)"`.
  - `CATEGORY` is one of `"BFL"` (generation), `"BFL/Finetune"`, `"BFL/Utility"`, `"BFL/Utils"`, `"BFL/Config"`. Match the existing module's choice.
  - A brand-new module file under `nodes/` is invisible until its name is appended to `node_list` in `__init__.py:4-9`.
- **Logging**: every outbound request and every status line is prefixed `[BFL] ` so it's grep-able in the ComfyUI console.
- **curl-equivalent**: every POST prints the full curl-equivalent (URL, headers, body) before sending. Matches the pattern in `nodes/base.py:60-62`. Useful for users debugging the BFL API directly.
- **Width / height validation**: when a node takes `width` / `height` ints, the request path runs `self.check_multiple_of_32(width, height)` (already called by `BaseFlux.generate_image` if they're in `arguments`). Newer Flux 2 / Ultra models use `aspect_ratio` strings (`"16:9"`, `"1:1"`, …) and bypass dimension validation.
- **Seed handling**: `seed = -1` means *random*. The node parameter defaults to `-1`. Only insert `arguments["seed"] = seed` into the request body when `seed != -1` — never send `-1` to BFL.
- **Optional argument inclusion**: build the request `arguments` dict with required keys, then conditionally add optional ones only when non-default / non-empty (`if webhook_url:`, `if image_prompt:`, …). Matches every node in `nodes/api_node.py`.
- **Graceful failure**: on any unhandled exception, on terminal API status (`Error`, `Content Moderated`, `Request Moderated`), or on polling exhaustion, return `self.create_blank_image()` — a black 512×512 IMAGE tensor. ComfyUI workflows must never crash because of a BFL failure.
- **Polling**: 5-second interval, max 40 attempts (~200 s ceiling). Already implemented in `BaseFlux.get_result` — do not write a second polling loop in a subclass.
- **Config resolution**: every generation node accepts an optional `config` input of type `BFL_CONFIG` (the output of `FluxConfig_BFL`). Pass it through to `super().generate_image(url_path, arguments, config)`; the base class hands it to `get_config_loader(config)` from `nodes/config_node.py:57-67`, which decides whether to use the `config.ini`-backed default loader or build one from the override. **Both paths must work** — `config=None` (use file) and `config=<dict>` (override).
- **Conventional Commits 1.0.0**: `<type>[scope][!]: <description>`. Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `perf`, `test`, `build`, `ci`. Scopes: `api`, `finetune`, `config`, `utils`, `web`, `docs`, `release`, `tooling`. Description: lowercase, imperative ("add", not "added"/"adds"), no trailing period, ≤ 72 chars. Body explains *why*, wrapped at 72. Use `!` after type/scope for breaking changes. No Jira prefix. **No `Co-Authored-By: Claude` / "Generated with…" footer.** Do NOT inspect `git log` to derive style — historical commits used `update:` and similar non-standard types; the new standard starts now.
- **Version bumps**: edit `pyproject.toml` `version` field only. Commit message: `chore(release): bump version to X.Y.Z`.

### Never do

- **Never** commit a real `X_KEY` in `config.ini`. The tracked placeholder must stay `your-key`. A PreToolUse hook (`block-api-key-commit.sh`) blocks Edit/Write to `config.ini` with any other value. If the user needs a real key locally, they edit it after clone and the placeholder stays in the repo.
- **Never** log the full `x-key` header value, webhook secret, or BFL API response body that contains either.
- **Never** call BFL endpoints from `nodes/utils.py` or other helper modules. Network I/O lives inside generation / finetune / credits node classes only.
- **Never** bypass hooks with `--no-verify`. Fix the underlying issue.
- **Never** auto-commit. The user runs `/commit`.
- **Never** add a dependency to `requirements.txt` / `pyproject.toml` without an explicit user ask — the package currently depends only on `torch` (transitively on `requests`, `Pillow`, `numpy` via ComfyUI). Keep it that way.
- **Never** edit `web/js/` "while I'm here". The ComfyUI frontend extensions are sensitive to ComfyUI version drift; touch them only when the user asks for a UI change.

### Gotchas

- `ConfigLoader` in `nodes/config.py:85-86` constructs a module-level singleton `config_loader` at import time. Some nodes still reference that singleton; new code should use `get_config_loader(config)` from `nodes/config_node.py:57-67` (which respects the per-call override) instead.
- `BASE_URL` in `config.ini` may or may not end with `/`. `ConfigLoader.create_url` uses `urljoin` — pass the `path` argument **without** a leading slash, otherwise `urljoin` will strip the existing prefix path.
- **Finetune endpoints are regional**: `api.us.bfl.ai`, `api.eu.bfl.ai`. The default `api.bfl.ai/v1/` does **not** serve finetune routes. Region selection is via `FluxConfig_BFL`'s `region` field or per-call. See `nodes/finetune.py`.
- BFL's async pattern: POST to `flux-pro-1.1` (etc.) returns `{"id": "<task_id>"}`. Polling GET goes to `get_result?id=<task_id>` — note: **query parameter `id`**, not a path segment. `BaseFlux.get_result` already builds this correctly; if you write a one-off polling call, match it.
- The newer Flux 2 / Klein nodes (`nodes/api_node.py` lower half) sometimes inline `self.post_request` + `self.get_result` instead of calling `super().generate_image(...)`. Both styles exist in the codebase; if you're scaffolding a new node, **prefer `super().generate_image(...)`** — it's shorter and runs the dimension check for you.
- `__init__.py` does dynamic import of every entry in `node_list`. A new node file in `nodes/<name>.py` is invisible to ComfyUI until you append `"<name>"` to that list.
- `WEB_DIRECTORY = "./web"` in `__init__.py:21` exposes `web/js/*` to ComfyUI's frontend. Renaming or moving `web/` breaks the frontend extensions silently — they just won't load.
