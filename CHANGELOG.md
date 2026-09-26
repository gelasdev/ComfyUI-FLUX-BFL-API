# Changelog

All notable changes to this project from v1.1.0 onward are documented in this file. Earlier history lives in `git log`.

## [Unreleased]

### Added

| Node / Feature | Endpoint | Notes |
|---|---|---|
| Flux Video Edit (BFL) | `POST /v1/flux-tools/video-edit-v1` | FLUX Video Edit [fast]: `video` (MP4 URL or base64, ≤ 15 s / 50 MiB) + edit `prompt` + `safety_tolerance` (0–4). The endpoint rejects every other field (no seed, webhook or generation controls), so none are exposed. Duration, aspect ratio and audio follow the source; output is 720p. Outputs `VIDEO`, shares the Flux 3 Video polling ceiling. |
| Flux Video Upscale (BFL) | `POST /v1/flux-tools/video-upscale-v1` | BFL release 2026-08-20. `input_video` (≤ 20 s, 50 MB, 2560×1440), `upscale_factor` (1.5–3, default 2), `creativity` (0 precise / 1 creative, default 1), optional `prompt`, `safety_tolerance` (0–4), webhook. Outputs `VIDEO`. |
| Flux Deblur (BFL) | `POST /v1/flux-tools/deblur-v1` | BFL release 2026-06-25. Single `image` (base64 or URL, ≤ 4 MP), no prompt or mask; `safety_tolerance` (0–5), `output_format` (png default), `seed`, webhook. |
| `qhd` / `uhd` resolution on Flux 3 Video T2V / I2V / V2V | `POST /v1/flux-3-video` | BFL release 2026-09-10: 2K (2560×1440) and 4K (3840×2176) at 16:9 from a single request. |
| `disable_pup` on Flux 2 Max / Pro / Pro Preview | `POST /v1/flux-2-{max,pro,pro-preview}` | Turns off the automatic prompt upsampling these models apply by default. Only sent when enabled. |
| `safety_tolerance` and `disable_pup` on Flux Outpaint (BFL) | `POST /v1/flux-tools/outpainting-v1` | Both were in the API schema but not exposed. Only sent when changed from the defaults (2 / false). |
| Example workflow groups | — | `BFL-API-tools.json`: a **Flux Deblur** group (Load Image → Image to Base64 → Flux Deblur → Preview). `BFL-API-flux-3-video.json`: **FLUX Video Edit** and **FLUX Video Upscale** groups (Load Video → Video to Base64 → node → Save Video). Appended only — existing nodes, links and groups are unchanged; new groups are bypassed like the rest. |
| Moderation / error details in the polling log | `GET /v1/get_result` | On a terminal status (`Error`, `Request Moderated`, `Content Moderated`) the `details` payload is printed — for moderation it carries the `Moderation Reasons` categories added by BFL on 2026-06-15. |

### Fixed

| Issue | Detail |
|---|---|
| Fresh Flux 2 nodes failed validation | All seven Flux 2 nodes defaulted `width` / `height` to `0` (meaning "not sent — BFL picks the size") but declared `min: 64`, so ComfyUI rejected every new Flux 2 node, and the Pro Preview / Klein 9B Preview example groups, with *"Value 0 smaller than min of 64"* until both were changed by hand. `min` is now `0` with a tooltip; `0` is still omitted from the request and any other value is sent as before. |
| Finetune example workflow needed a third-party node pack | `BFL-API-finetune.json` used `ShowText\|pysssss` (ComfyUI-Custom-Scripts) to display results, plus an unused `My Finetunes` group-node template — both surfaced as "Missing Node Packs" on load. The four display nodes are now ComfyUI's core **Preview as Text** (`PreviewAny`), the stale template is removed, and the four utility groups are resized to fit. Verified in ComfyUI 0.37.0 (frontend 1.52.7). |
| Flux 3 Video V2V offered 16–20 s durations | BFL capped video continuation at 15 s on 2026-08-17; longer values returned 422 and a blank video. The V2V `duration` list now stops at 15. T2V / I2V stay at 20. |
| `draft: true` with a non-`hd` resolution was rejected | Drafts always render at `hd` and BFL rejects any other resolution with `draft`. The node now logs a warning and sends the draft at `hd` instead of wasting the request. |

## [1.4.0] — 2026-08-06

### Added

| Node / Feature | Endpoint | Notes |
|---|---|---|
| Flux 3 Video T2V (BFL) | `POST /v1/flux-3-video` | Text-to-video (`mode: t2v`), up to 20 s with synchronized audio. Knobs: `resolution` (hd / fhd), `duration` (auto or 5–20 s), `aspect_ratio`, `generate_audio`, `safety_tolerance` (0–4), `draft` (fast preview). Outputs ComfyUI's native `VIDEO` type; polling ceiling raised to 240 attempts (~20 min) for video — a real v2v+fhd task was still generating at 11 min. |
| Flux 3 Video I2V (BFL) | `POST /v1/flux-3-video` | Image-to-video (`mode: i2v`). Single `keyframes` string input: a bare image (base64/URL), a JSON array of images, or `[seconds, image]` pairs (up to 10). Warns when 3+ plain keyframes are sent with `duration: auto` (BFL requires a set duration). Same shared knobs as T2V. |
| Flux 3 Keyframes (BFL) | — | Utility: combines up to 10 image sockets (`start_image`, `image_2`–`image_9`, `end_image`) into the keyframes JSON string for I2V. Empty sockets are skipped. `timing: even` sends a plain list (first starts, last ends, middles spread evenly); `timing: custom` sends `[seconds, image]` pairs — the BFL schema allows no mixing, so `start_image` is auto-pinned at 0, middles use their `time_N` widgets, and `end_image` lands at `end_time` (with `duration: auto` that value is the clip length). Sorted into time order; warns on duplicate times or when `end_time` is not the largest. |
| Flux 3 Video V2V (BFL) | `POST /v1/flux-3-video` | Video continuation (`mode: v2v`) from `start_video` (MP4 URL or base64). Same shared knobs as T2V. |
| Video to Base64 (BFL) | — | Utility: converts a ComfyUI VIDEO input to a base64 MP4 string for V2V's `start_video`. Reads the stream source directly when it is already MP4 (in memory or on disk); other containers are remuxed to MP4 via `VideoInput.save_to`. |
| Flux Virtual Try-On v2 (BFL) | `POST /v1/flux-tools/vto-v2` | VTO v2 (BFL release 2026-07-17): sharper face preservation and garment detail, inputs up to 4 MP. Identical request/response format to v1 — implemented as a subclass overriding only the endpoint path. |

### Fixed

| Issue | Detail |
|---|---|
| `'Generating' is not a valid Status` during polling | BFL's `get_result` reference documents two intermediate statuses the `Status` enum was missing: `Reasoning` and `Generating` (seen on FLUX 3 tasks). Both are now treated like `Pending` (wait 5 s, retry) instead of tripping the ValueError handler with a misleading "JSON parsing error" log. |

## [1.3.0] — 2026-06-25

### Added

| Node / Feature | Endpoint | Notes |
|---|---|---|
| `mode` on Flux Outpaint (BFL) | `POST /v1/flux-tools/outpainting-v1` | Quality/speed tradeoff added by BFL on 2026-06-09. Exposed as a combo defaulting to `high` (the API default); only sent when set to `fast`, so the default request body is unchanged. |

## [1.2.0] — 2026-06-01

### Added

| Node / Feature | Endpoint | Notes |
|---|---|---|
| Flux Virtual Try-On (BFL) | `POST /v1/flux-tools/vto-v1` | Dress a person image with a garment image. Base64 string inputs for `person` and `garment`, a required `prompt`, and optional `safety_tolerance` (0–5), `output_format` (jpeg / png), `seed`, `webhook_url`, `webhook_secret`. Follows the shared `BaseFlux` post → poll path. Two virtual try-on groups added to the tools example workflow. |

## [1.1.0] — 2026-05-25

### Added

| Node / Feature | Endpoint | Notes |
|---|---|---|
| Flux Erase (BFL) | `POST /v1/flux-tools/erase-v1` | Object removal via base64 image + binary mask. White pixels in the mask are erased; black pixels are kept. Knobs: `dilate_pixels` (0–25, default 10), `safety_tolerance` (0–5), `output_format` (png / jpeg), `seed`, `webhook_url`, `webhook_secret`. |
| Flux Outpaint (BFL) | `POST /v1/flux-tools/outpainting-v1` | Image extension to a target canvas. Knobs: `width` / `height` (≥64, step 32), `center_reference` (toggle), `reference_offset_x` / `reference_offset_y`, optional `prompt`, `auto_crop`, `output_format` (png / jpeg). |
| `image_format` on Image to Base64 (BFL) | — | New optional dropdown: `jpeg` (default, backward-compatible) or `png` (lossless, recommended for masks fed into Flux Erase / Flux Pro Fill). |

### Fixed

| Issue | Detail |
|---|---|
| Workflow crash on non-multiple-of-32 width/height | `BaseFlux.generate_image` now catches `check_multiple_of_32`'s `ValueError` inside its try/except and returns a blank image, matching the rest of the graceful-failure path. |
| `FluxErase` `image` / `mask` defaulted to `None` | Defaults are now `""` — prevents JSON-null serialization when the socket is left unwired. Consistent with `FluxOutpaint`'s `input_image` default. |
| Whitespace-only prompts on Flux Outpaint | Prompts that contain only whitespace are no longer forwarded — `if prompt and prompt.strip():` strips the no-op case. |
