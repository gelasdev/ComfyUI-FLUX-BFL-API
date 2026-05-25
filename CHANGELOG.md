# Changelog

All notable changes to this project from v1.1.0 onward are documented in this file. Earlier history lives in `git log`.

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
