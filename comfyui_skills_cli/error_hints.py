"""Common error pattern matching — maps ComfyUI errors to actionable hints."""

from __future__ import annotations

import re

# Common error patterns → actionable hints
# Each entry is (pattern, hint) where pattern is either a plain string (checked
# via substring match) or a compiled regex (checked via regex search).
_ERROR_HINTS: list[tuple[str | re.Pattern[str], str]] = [
    # --- Cloud API ---
    (
        "Unauthorized: Please login first",
        "This workflow uses ComfyUI cloud API nodes. "
        "Configure a ComfyUI API Key: (1) Go to https://platform.comfy.org to generate a key, "
        '(2) Add it to server settings via Web UI or config.json "comfy_api_key" field.',
    ),
    # --- Missing model files (specific types first) ---
    (
        re.compile(r"vae.*(?:not found|no such file)", re.IGNORECASE),
        "A required VAE model is missing. "
        "Run `comfyui-skill deps check <workflow_id>` to identify missing models.",
    ),
    (
        re.compile(r"clip.*(?:not found|no such file)", re.IGNORECASE),
        "A required CLIP model is missing. "
        "Run `comfyui-skill deps check <workflow_id>` to identify missing models.",
    ),
    (
        re.compile(r"lora.*(?:not found|no such file)", re.IGNORECASE),
        "A required LoRA model is missing. "
        "Run `comfyui-skill deps check <workflow_id>` to identify missing models.",
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
    # --- Custom nodes ---
    (
        re.compile(
            r"cannot find class|class_type not found|node not found", re.IGNORECASE
        ),
        "A required custom node is not installed. "
        "Run `comfyui-skill deps check <workflow_id>` to identify missing nodes.",
    ),
    # --- Workflow validation ---
    (
        re.compile(r"prompt is not valid|invalid prompt", re.IGNORECASE),
        "The workflow has validation errors. "
        "Run `comfyui-skill run <workflow_id> --validate` to see details.",
    ),
    # --- Connection errors ---
    (
        "Connection refused",
        "ComfyUI server is not running. Start ComfyUI and try again.",
    ),
    (
        re.compile(r"timed?\s*out|timeout", re.IGNORECASE),
        "Connection to ComfyUI server timed out. "
        "Check if the server is running and accessible.",
    ),
    # --- GPU / memory errors ---
    (
        "CUDA out of memory",
        "GPU memory exhausted. Run `comfyui-skill free` to release VRAM, then retry.",
    ),
    (
        "MPS out of memory",
        "GPU memory exhausted. Run `comfyui-skill free` to release VRAM, then retry.",
    ),
    (
        re.compile(r"CUDA error|CUDA driver|no CUDA GPUs", re.IGNORECASE),
        "GPU driver error. Check that CUDA drivers are installed and compatible "
        "with your PyTorch version.",
    ),
    # --- General file errors (least specific, must be last) ---
    (
        re.compile(r"FileNotFoundError|No such file or directory", re.IGNORECASE),
        "A required file is missing. Check that all model files and inputs "
        "are in the correct directories.",
    ),
]


def match_error_hint(error_msg: str) -> str:
    lower = error_msg.lower()
    for pattern, hint in _ERROR_HINTS:
        if isinstance(pattern, re.Pattern):
            if pattern.search(error_msg):
                return hint
        else:
            if pattern.lower() in lower:
                return hint
    return ""
