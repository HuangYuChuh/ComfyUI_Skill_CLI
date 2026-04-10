"""comfyui-skill queue — view and manage the ComfyUI execution queue."""

from __future__ import annotations

from typing import List

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
def queue_list(ctx: typer.Context):
    """Show running and pending jobs in the queue."""
    client, server_id = _build_client(ctx)

    try:
        queue = client.get_queue()
        running = [
            {"prompt_id": item[1], "status": "running"}
            for item in queue.get("queue_running", [])
            if len(item) > 1
        ]
        pending = [
            {"prompt_id": item[1], "status": "pending", "position": i}
            for i, item in enumerate(queue.get("queue_pending", []))
            if len(item) > 1
        ]
        output_result(ctx, {
            "server_id": server_id,
            "running": running,
            "pending": pending,
        })
    except Exception as exc:
        output_error(ctx, "QUEUE_FAILED", f"Failed to get queue: {exc}")


@app.command("clear")
def queue_clear(ctx: typer.Context):
    """Clear all pending jobs from the queue (does not stop running jobs)."""
    client, server_id = _build_client(ctx)

    try:
        client.queue_clear()
        output_result(ctx, {"status": "cleared", "server_id": server_id})
    except Exception as exc:
        output_error(ctx, "QUEUE_FAILED", f"Failed to clear queue: {exc}")


@app.command("delete")
def queue_delete(
    ctx: typer.Context,
    prompt_ids: List[str] = typer.Argument(help="Prompt IDs to remove from queue"),
):
    """Remove specific jobs from the pending queue."""
    client, server_id = _build_client(ctx)

    try:
        client.queue_delete(prompt_ids)
        output_result(ctx, {"status": "deleted", "prompt_ids": prompt_ids, "server_id": server_id})
    except Exception as exc:
        output_error(ctx, "QUEUE_FAILED", f"Failed to delete from queue: {exc}")
