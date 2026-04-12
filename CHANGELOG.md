# Changelog

## 0.2.7

### New Commands

- `nodes list / info / search` — discover available ComfyUI nodes, inspect input/output schemas, search by name or category
- `server stats` — show VRAM, RAM, GPU, ComfyUI/Python/PyTorch versions (`--all` for multi-server comparison)
- `server features` — query server capability flags
- `jobs list / show` — server-side job history with status filtering and pagination
- `logs show` — access ComfyUI server logs for error diagnosis
- `templates list / subgraphs` — discover workflow templates and reusable subgraph components
- `models embeddings` — list installed text embeddings
- `models metadata` — inspect safetensors model metadata

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
- Fix double error output in `models metadata` when file not found
