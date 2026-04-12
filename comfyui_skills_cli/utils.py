"""Shared utilities for command modules."""
from __future__ import annotations

from typing import Any

import typer

from .client import ComfyUIClient
from .config import get_base_dir, get_default_server_id, get_server, load_config
from .output import output_error


def build_client(ctx: typer.Context) -> tuple[ComfyUIClient, str]:
    """Build a ComfyUIClient from context. Exits on error."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)
    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        raise typer.Exit(code=1)  # Safety net — output_error already exits, but be explicit
    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )
    return client, server_id
