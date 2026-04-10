"""comfyui-skill free — release GPU memory and unload models."""

from __future__ import annotations

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import output_error, output_result


def free_cmd(
    ctx: typer.Context,
    models: bool = typer.Option(False, "--models", "-m", help="Unload all models from VRAM"),
    memory: bool = typer.Option(False, "--memory", help="Free all cached memory"),
):
    """Release GPU memory. With no flags, unloads models and frees memory."""
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

    # Default: both if no flag specified
    if not models and not memory:
        models = True
        memory = True

    try:
        client.free_memory(unload_models=models, free_memory=memory)
        actions = []
        if models:
            actions.append("models_unloaded")
        if memory:
            actions.append("memory_freed")
        output_result(ctx, {"status": "ok", "actions": actions, "server_id": server_id})
    except Exception as exc:
        output_error(ctx, "FREE_FAILED", f"Failed to free memory: {exc}")
