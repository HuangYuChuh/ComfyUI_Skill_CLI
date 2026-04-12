"""comfyui-skill queue — view and manage the ComfyUI execution queue."""

from __future__ import annotations

from typing import List

import typer

from ..output import output_error, output_result
from ..utils import build_client

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def queue_list(ctx: typer.Context):
    """Show running and pending jobs in the queue."""
    client, server_id = build_client(ctx)

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
        return


@app.command("clear")
def queue_clear(ctx: typer.Context):
    """Clear all pending jobs from the queue (does not stop running jobs)."""
    client, server_id = build_client(ctx)

    try:
        client.queue_clear()
        output_result(ctx, {"status": "cleared", "server_id": server_id})
    except Exception as exc:
        output_error(ctx, "QUEUE_FAILED", f"Failed to clear queue: {exc}")
        return


@app.command("delete")
def queue_delete(
    ctx: typer.Context,
    prompt_ids: List[str] = typer.Argument(help="Prompt IDs to remove from queue"),
):
    """Remove specific jobs from the pending queue."""
    client, server_id = build_client(ctx)

    try:
        client.queue_delete(prompt_ids)
        output_result(ctx, {"status": "deleted", "prompt_ids": prompt_ids, "server_id": server_id})
    except Exception as exc:
        output_error(ctx, "QUEUE_FAILED", f"Failed to delete from queue: {exc}")
        return
