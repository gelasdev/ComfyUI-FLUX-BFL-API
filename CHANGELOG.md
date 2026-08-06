# Changelog

All notable changes to this project from v1.1.0 onward are documented in this file. Earlier history lives in `git log`.

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
