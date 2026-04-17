# Changelog

## 0.2.10

### Improvements

- `run` / `submit` now auto-upload local image files referenced by image-type parameters. An explicit filesystem path (absolute, `./`, `../`, or `~/...`) is uploaded to the ComfyUI server and rewritten to the server-side reference before the workflow is queued. Bare filenames (`cat.png`) and subfolder refs (`clipspace/foo.png`) still resolve on the server — they are never replaced with whatever happens to sit in the caller's cwd.
- Upload failures surface as a hard `UPLOAD_FAILED` error instead of submitting with a broken path and returning an obscure ComfyUI 400.

### Fixes

- `status` command now downloads output files to the local `outputs/` directory, matching the behaviour of synchronous `run`. Previously `submit` + `status` returned filenames in the response but no files on disk, breaking multi-step agent pipelines.
- Sync `__version__` in `comfyui_skills_cli/__init__.py` with `pyproject.toml` (they had drifted apart across releases).

## 0.2.9

### Fixes

- `workflow import --from-server` now works on ComfyUI 0.19.0. Two independent bugs were fixed: `/v2/userdata` uses `path` (not `dir`) and returns a list of dicts rather than strings, and `/userdata/{file}` is a single-segment aiohttp route so the relative path must be fully percent-encoded (including `/` separators). Reported and patched by @DanielBoettner in #28.

## 0.2.8

### New Flags

- `workflow import --type video` — parameter-detection preset for video workflows. Exposes `format`, `codec`, `frame_rate`, `fps`, `noise_seed`, `cfg`.

### Fixes

- Video output is now correctly classified as `media_type: "video"` instead of `"image"`. ComfyUI's `SaveVideo` / `PreviewVideo` nodes report video files under the `"images"` history key, so media type is now inferred from the file extension. Also removes dead `"gifs"` and `"video"` entries from `_MEDIA_KEYS` (only `"images"` and `"audio"` are ever populated).

### Docs

- Added Korean (`README.ko.md`) and Spanish (`README.es.md`) README translations. All six language versions are now cross-linked: English, 简体中文, 繁體中文, 日本語, 한국어, Español.

## 0.2.7

### New Commands

- `nodes list / info / search` — discover available ComfyUI nodes, inspect input/output schemas, search by name or category
- `server stats` — show VRAM, RAM, GPU, ComfyUI/Python/PyTorch versions (`--all` for multi-server comparison)
- `jobs list / show` — server-side job history with status filtering and pagination
- `logs show` — access ComfyUI server logs for error diagnosis
- `templates list / subgraphs` — discover workflow templates and reusable subgraph components

### New Flags

- `run / submit --priority` — heap-based queue ordering (lower = first, negative = jump queue)
- `run --validate` — dry-run workflow validation without GPU execution
- `run / submit --only` — partial execution via `partial_execution_targets`
- `upload --mask` — upload inpainting masks via `/upload/mask`

### Improvements

- `run` command now uses WebSocket streaming for real-time progress events instead of HTTP polling (auto-falls back to polling if unavailable)
- `workflow import` now detects deprecated nodes and suggests replacements via `/node_replacements`
- Added `websocket-client` to dependencies

### Fixes

- Handle `None` values in `/object_info` category and display_name fields
