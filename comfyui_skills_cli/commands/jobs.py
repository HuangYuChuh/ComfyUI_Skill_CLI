"""comfyui-skill jobs — server-side job history."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import get_output_format, OutputFormat, output_error, output_result

app = typer.Typer(no_args_is_help=True)


def _build_client(ctx: typer.Context) -> ComfyUIClient:
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')

    return ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )


@app.command("list")
def jobs_list(
    ctx: typer.Context,
    status: Optional[str] = typer.Option(None, "--status", help="Filter: pending, in_progress, completed, failed"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max entries to return"),
    sort: str = typer.Option("created_at", "--sort", help="Sort field"),
):
    """List jobs from the ComfyUI server."""
    client = _build_client(ctx)
    try:
        data = client.get_jobs(status=status or "", limit=limit, sort_by=sort)
    except Exception as exc:
        output_error(ctx, "JOBS_FAILED", f"Failed to fetch jobs: {exc}")

    fmt = get_output_format(ctx)
    if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
        output_result(ctx, data)
        return

    # Text mode — render a table
    jobs = data if isinstance(data, list) else data.get("jobs", data.get("items", []))
    if not jobs:
        Console().print("[dim]No jobs found.[/dim]")
        return

    table = Table(show_lines=True)
    table.add_column("prompt_id")
    table.add_column("status")
    table.add_column("created_at")
    table.add_column("duration")

    for job in jobs:
        prompt_id = str(job.get("prompt_id", job.get("id", "")))[:12]
        job_status = job.get("status", "")
        created = job.get("created_at", "")
        duration = job.get("duration", job.get("execution_time", ""))
        table.add_row(prompt_id, job_status, str(created), str(duration))

    Console().print(table)


@app.command("show")
def jobs_show(
    ctx: typer.Context,
    prompt_id: str = typer.Argument(help="Prompt ID or job ID to look up"),
):
    """Show details of a specific job (falls back to history API)."""
    client = _build_client(ctx)

    # Try jobs API first, then history
    try:
        data = client.get_job(prompt_id)
    except Exception:
        data = None

    if data is None:
        try:
            data = client.get_history(prompt_id)
        except Exception as exc:
            output_error(ctx, "JOBS_FAILED", f"Failed to fetch job: {exc}")

    if data is None:
        output_error(ctx, "NOT_FOUND", f'Job "{prompt_id}" not found.')

    fmt = get_output_format(ctx)
    if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
        output_result(ctx, data)
        return

    # Text mode
    console = Console()
    if isinstance(data, dict):
        for key, value in data.items():
            console.print(f"[bold]{key}:[/bold] {value}")
    else:
        console.print(data)
