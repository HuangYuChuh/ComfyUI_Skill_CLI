"""comfyui-skill upload — upload files to ComfyUI server."""

from __future__ import annotations

import os

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import output_error, output_result


def upload_cmd(
    ctx: typer.Context,
    file_path: str = typer.Argument(help="Path to file (image, mask, audio, etc.)"),
):
    """Upload a file to ComfyUI for use in workflows (e.g., images, masks, audio)."""
    if not os.path.isfile(file_path):
        output_error(ctx, "FILE_NOT_FOUND", f'File not found: "{file_path}"')
        return

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )

    try:
        result = client.upload_file(file_path)
        output_result(ctx, {
            "name": result.get("name", ""),
            "subfolder": result.get("subfolder", ""),
            "type": result.get("type", "input"),
            "server_id": server_id,
        })
    except Exception as exc:
        output_error(ctx, "UPLOAD_FAILED", f"Upload failed: {exc}")
