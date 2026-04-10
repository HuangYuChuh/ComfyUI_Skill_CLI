"""comfyui-skill models — discover available models on ComfyUI server."""

from __future__ import annotations

from typing import Optional

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import output_error, output_result

app = typer.Typer(no_args_is_help=True)


def _build_client(ctx: typer.Context) -> tuple[ComfyUIClient, str]:
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')

    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )
    return client, server_id


@app.command("list")
def models_list(
    ctx: typer.Context,
    folder: Optional[str] = typer.Argument(None, help="Model folder (e.g., checkpoints, loras, vae). Omit to list all folders."),
):
    """List available models. Specify a folder to see its contents, or omit to list all folders."""
    client, server_id = _build_client(ctx)

    try:
        if folder:
            models = client.get_models(folder)
            output_result(ctx, {
                "server_id": server_id,
                "folder": folder,
                "models": models,
                "count": len(models),
            })
        else:
            folders = client.get_model_folders()
            output_result(ctx, {
                "server_id": server_id,
                "folders": folders,
            })
    except Exception as exc:
        output_error(ctx, "MODELS_FAILED", f"Failed to list models: {exc}")
