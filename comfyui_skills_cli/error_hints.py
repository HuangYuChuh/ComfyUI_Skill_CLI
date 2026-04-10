"""Common error pattern matching — maps ComfyUI errors to actionable hints."""

from __future__ import annotations

# Common error patterns → actionable hints
_ERROR_HINTS: list[tuple[str, str]] = [
    (
        "Unauthorized: Please login first",
        "This workflow uses ComfyUI cloud API nodes. "
        "Configure a ComfyUI API Key: (1) Go to https://platform.comfy.org to generate a key, "
        '(2) Add it to server settings via Web UI or config.json "comfy_api_key" field.',
    ),
    (
        "ckpt",
        "A required model file is missing. "
        "Run `comfyui-skill deps check <workflow_id>` to identify missing models.",
    ),
    (
        "safetensors",
        "A required model file is missing. "
        "Run `comfyui-skill deps check <workflow_id>` to identify missing models.",
    ),
    (
        "Connection refused",
        "ComfyUI server is not running. Start ComfyUI and try again.",
    ),
    (
        "CUDA out of memory",
        "GPU memory exhausted. Run `comfyui-skill free` to release VRAM, then retry.",
    ),
    (
        "MPS out of memory",
        "GPU memory exhausted. Run `comfyui-skill free` to release VRAM, then retry.",
    ),
]


def match_error_hint(error_msg: str) -> str:
    lower = error_msg.lower()
    for pattern, hint in _ERROR_HINTS:
        if pattern.lower() in lower:
            return hint
    return ""
