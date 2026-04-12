"""comfyui-skill logs — access ComfyUI server logs."""

from __future__ import annotations

import typer

from ..output import output_error, output_result
from ..utils import build_client

app = typer.Typer(no_args_is_help=True)


@app.command("show")
def logs_show(
    ctx: typer.Context,
    lines: int = typer.Option(50, "--lines", "-n", help="Number of recent log lines to show"),
):
    """Show recent ComfyUI server logs."""
    client, server_id = build_client(ctx)

    try:
        data = client.get_logs()
        entries = data.get("entries", [])
        recent = entries[-lines:] if len(entries) > lines else entries
        output_result(ctx, {
            "server_id": server_id,
            "total_entries": len(entries),
            "showing": len(recent),
            "entries": recent,
        })
    except Exception as exc:
        output_error(ctx, "LOGS_FAILED", f"Failed to fetch logs: {exc}")
        return
