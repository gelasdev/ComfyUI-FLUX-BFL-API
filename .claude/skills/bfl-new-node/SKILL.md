---
name: bfl-new-node
description: Scaffold a new ComfyUI node that wraps a BFL FLUX endpoint — picks the right base class, writes INPUT_TYPES + generate_image, registers the class in NODE_CLASS_MAPPINGS / NODE_DISPLAY_NAME_MAPPINGS, and updates the README. Follow this when adding a Flux model, finetune variant, or utility node.
when_to_use: User says "new node", "add a Flux N model", "wrap the X endpoint", "scaffold a BFL node", "add a finetune node", or invokes the /new-node command.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(rg:*), Bash(grep:*)
argument-hint: <ClassName> [generation|finetune|utility] [endpoint-name]
---

# BFL new-node scaffold

Adds a single ComfyUI node that follows every convention in `CLAUDE.md`. This skill **writes files**.

## Decisions you make up front

If `$ARGUMENTS` doesn't already say:

1. **ClassName** (Python identifier, bare, no `_BFL` suffix). Example: `Flux3`, `FluxPro2Ultra`.
2. **Kind**:
   - `generation` → inherits `BaseFlux`, category `"BFL"`, lives in `nodes/api_node.py`.
   - `finetune` → inherits `BaseFinetuneFlux`, category `"BFL/Finetune"`, lives in `nodes/finetune.py`.
   - `utility` → inherits `object`, category `"BFL/Utility"` or `"BFL/Utils"`, lives in `nodes/utils.py` or a new file.
3. **Endpoint name** (generation/finetune only): the BFL API path segment, e.g. `flux-pro-1.1`, `flux-dev`, `flux-2-pro`. Used in `super().generate_image("<endpoint>", arguments, config)`.
4. **Dimension style** (generation only):
   - `dims` → required `width` / `height` ints (multiples of 32). Older Flux models.
   - `aspect_ratio` → required `aspect_ratio` enum string. Newer Flux 2 / Ultra family.
   - Pick one. Do not mix.

If any of those is missing, ask once at the top before scaffolding.

## What you write

### Class body

For a `generation` node with `dims`:

```python
class <ClassName>(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "image_prompt": ("STRING", {"default": ""}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",),
            },
        }

    def generate_image(self, prompt, width, height, prompt_upsampling, safety_tolerance, output_format,
                       seed=-1, image_prompt="", webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
        }
        if seed != -1:
            arguments["seed"] = seed
        if image_prompt:
            arguments["image_prompt"] = image_prompt
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("<endpoint>", arguments, config)
```

For `aspect_ratio` instead of dims, replace the dims block in `INPUT_TYPES` with:

```python
"aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
```

…and in `generate_image`, replace the `"width"`, `"height"` lines with `"aspect_ratio": aspect_ratio`.

**Always prefer `super().generate_image(...)`** over inlining `self.post_request` + `self.get_result` — the base class runs `check_multiple_of_32` for you when dims are present. (Some Flux 2 nodes inline both, but for new code the super call is shorter and safer.)

### Registration

At the bottom of the target module, in the existing dicts:

```python
NODE_CLASS_MAPPINGS = {
    ...,
    "<ClassName>_BFL": <ClassName>,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    ...,
    "<ClassName>_BFL": "<Human Readable Name> (BFL)",
}
```

The `_BFL` suffix on the dict key is mandatory. The ` (BFL)` suffix on the display name is mandatory. The Python class name itself is bare — no `_BFL`.

### README update

Append a row to the right table in `README.md`:
- Generation → "### Generation" table
- Finetune → "### Finetune" table
- Utility → "### Utils" or "### Config" table (whichever matches CATEGORY)

Format: `| <Display Name> (BFL) | <one-sentence description> |`

### `__init__.py` (only if new module file)

If you create a new file under `nodes/`, append its module name (without `.py`) to `node_list` in `__init__.py:4-9`. If you're adding to an existing module (`api_node.py`, `finetune.py`, `utils.py`, `config_node.py`), do nothing.

## Verification before declaring done

1. `ruff check nodes/<modified-file>.py` — clean (the post-edit hook also runs this).
2. The new entry appears in BOTH `NODE_CLASS_MAPPINGS` AND `NODE_DISPLAY_NAME_MAPPINGS` with **matching keys**.
3. The registry key ends in `_BFL` and the display name ends in ` (BFL)`.
4. The new class inherits from the right base (`BaseFlux` / `BaseFinetuneFlux` / `object`).
5. `seed` is in `optional` with default `-1`, and the request body only includes it when `!= -1`.
6. `config: BFL_CONFIG` is in `optional` and is passed through to `super().generate_image(...)`.
7. If new module file was created, it's in `__init__.py`'s `node_list`.
8. README node table includes the new row.

## What this skill does NOT do

- Does NOT commit. The user runs `/commit` after.
- Does NOT bump version. The user runs `/version-bump` when releasing.
- Does NOT touch `web/js/` — the default ComfyUI UI renders the new node automatically.
- Does NOT add dependencies.
- Does NOT modify `nodes/base.py` — the base class is stable; do not "improve" it while here.

## Argument hint

`$ARGUMENTS` may carry: `ClassName`, kind (`generation` / `finetune` / `utility`), and endpoint name. Missing fields → ask once before scaffolding.
