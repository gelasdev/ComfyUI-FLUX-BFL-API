---
name: bfl-api-pattern
description: Reusable recipe for calling any BFL FLUX endpoint that follows the async POST → poll pattern. Use when integrating a new endpoint not covered by the existing BaseFlux methods, or when explaining how the existing flow works.
when_to_use: User asks "how does the BFL polling work?", "I want to call a new BFL endpoint that BaseFlux doesn't cover", "explain the request flow", or is debugging a 4xx/5xx response from BFL.
allowed-tools: Read, Grep, Glob
---

# BFL API request pattern

Every BFL FLUX generation / edit / fill / expand endpoint follows the same async shape. This skill documents it, and points to the existing implementation in `BaseFlux` (`nodes/base.py`).

**You should not write a new copy of this pattern**. The base class already implements it. This skill exists to (a) explain the existing flow to humans and (b) handle the rare case where a new endpoint needs a one-off variant (e.g. multipart upload, streaming response).

## The flow

1. **POST** to `<BASE_URL>/<endpoint>` with body JSON. Headers: `x-key: <API_KEY>`, `Content-Type: application/json`.
2. **Response**: `{ "id": "<task_id>" }` (or an error JSON if BFL rejects).
3. **Poll**: GET `<BASE_URL>/get_result?id=<task_id>` every **5 s**, max **40 attempts** (~200 s ceiling). Headers: same `x-key`.
4. **Status enum** (`nodes/status.py`):
   - `"Pending"` → retry.
   - `"Ready"` → response contains `result.sample` URL — download, convert to PIL, then tensor.
   - `"Error"` / `"Content Moderated"` / `"Request Moderated"` → terminal failure; return blank 512×512 black image.
   - `"Task not found"` → shouldn't happen mid-flow; treat as terminal.
5. **Image download & convert** (`BaseFlux.process_result`):
   - GET the `result.sample` URL (no auth needed; it's a signed S3-style URL).
   - Open with PIL.
   - Re-encode in the requested `output_format` (`jpeg` / `png`).
   - Convert to numpy float32 array `/ 255.0`.
   - Wrap in torch tensor with leading batch dim: `torch.from_numpy(arr)[None,]`.
   - Return as a 1-tuple matching `RETURN_TYPES = ("IMAGE",)`.

## Where this lives

| Step | Location |
|---|---|
| Build URL from base + path | `nodes/config.py:44-65` (`ConfigLoader.create_url`) |
| POST + curl print | `nodes/base.py:50-73` (`BaseFlux.post_request`) |
| Poll loop | `nodes/base.py:75-133` (`BaseFlux.get_result`) |
| Image → tensor | `nodes/base.py:19-38` (`BaseFlux.process_result`) |
| Graceful failure tensor | `nodes/base.py:40-44` (`BaseFlux.create_blank_image`) |
| Dimension check | `nodes/base.py:46-48` (`BaseFlux.check_multiple_of_32`) |
| Status enum | `nodes/status.py` |

## Headers

```python
headers = {"x-key": config_loader_instance.get_x_key()}
```

That's it. No `Authorization: Bearer`, no signed tokens. The `x-key` value is whatever's in `config.ini` `X_KEY` (or the override from `FluxConfig_BFL`).

## curl-equivalent print

Every outbound POST prints a copy-pasteable curl command before sending. Pattern from `nodes/base.py:60-62`:

```python
headers_str = " \\\n    ".join(f"-H '{k}: {v}'" for k, v in prepared.headers.items())
print(f"[BFL] curl -X POST '{prepared.url}' \\\n    {headers_str} \\\n    -d '{body}'")
```

This is intentional. Users who hit BFL errors paste the curl into a terminal to confirm whether the issue is the request or the response handling.

**Caveat**: this prints the `x-key` header. That's a known trade-off — the user is the only one looking at their own console. Do not log this header value to a file or send it anywhere.

## Regional endpoints (finetune only)

Default `BASE_URL` is `https://api.bfl.ai/v1/` and does NOT serve finetune routes. Finetune endpoints live at:
- `https://api.us.bfl.ai/v1/<path>`
- `https://api.eu.bfl.ai/v1/<path>`

`ConfigLoader.create_url(path, region=...)` (`nodes/config.py:44-65`) picks the right base. Region comes from `FluxConfig_BFL`'s `region` field or from the per-call argument.

## When you'd need to deviate from `BaseFlux`

You should reuse `BaseFlux` unless the endpoint:
- Uses multipart/form-data (not currently a thing in BFL).
- Streams the response (not currently a thing in BFL).
- Returns a non-image result that doesn't fit the `IMAGE` tensor (see `FluxCredits` in `nodes/api_node.py` — utility node, doesn't inherit BaseFlux, calls `requests.get` directly).
- Polls at a different interval (BFL doesn't currently require this).

If you really do need a one-off, mirror the existing patterns:
1. Print `[BFL] curl ...` before any outbound request.
2. Print `[BFL] <status>` lines.
3. On any exception or terminal status, return `self.create_blank_image()` (if `BaseFlux` subclass) or an equivalent safe value.

## What this skill does NOT do

- Does NOT write a new copy of `post_request` / `get_result`. The base class is the single source of truth.
- Does NOT change polling timing without explicit user ask.
- Does NOT log the `x-key` value to anywhere other than the user's console.
