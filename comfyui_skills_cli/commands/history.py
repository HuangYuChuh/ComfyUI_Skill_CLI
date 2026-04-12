"""comfyui-skill history list / show — execution history management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from ..config import get_base_dir, get_default_server_id, load_config
from ..output import OutputFormat, get_output_format, output_error, output_result
from ..utils import build_client

app = typer.Typer()


def _history_dir(base_dir: Path, server_id: str, workflow_id: str) -> Path:
    return base_dir / "data" / server_id / workflow_id / "history"


def _parse_skill_id(ctx: typer.Context, skill_id: str) -> tuple[str, str]:
    if "/" in skill_id:
        return skill_id.split("/", 1)
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    return server_id, skill_id


# ---------------------------------------------------------------------------
# history list
# ---------------------------------------------------------------------------

@app.command("list")
def history_list(
    ctx: typer.Context,
    skill_id: Optional[str] = typer.Argument(None, help="Skill ID (server_id/workflow_id). Required unless --server is used."),
    server: bool = typer.Option(False, "--server", help="Query the ComfyUI server instead of local files"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (server mode only)"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max entries to return"),
    sort: str = typer.Option("created_at", "--sort", help="Sort field (server mode only)"),
):
    """List execution history for a skill, or from the server."""

    if server:
        _list_server(ctx, status=status, limit=limit, sort=sort)
        return

    # Local mode — skill_id is required
    if skill_id is None:
        output_error(ctx, "MISSING_ARG", "skill_id is required when not using --server.")
        return

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    server_id, workflow_id = _parse_skill_id(ctx, skill_id)

    hist_dir = _history_dir(base_dir, server_id, workflow_id)
    if not hist_dir.exists():
        output_result(ctx, [])
        return

    entries = []
    for f in sorted(hist_dir.iterdir(), reverse=True):
        if not f.name.endswith(".json"):
            continue
        try:
            with open(f, encoding="utf-8") as fp:
                record = json.load(fp)
            entries.append({
                "run_id": record.get("run_id", f.stem),
                "status": record.get("status", "unknown"),
                "timestamp": record.get("timestamp", ""),
                "duration_ms": record.get("duration_ms", 0),
                "args": record.get("args", {}),
            })
        except (json.JSONDecodeError, OSError):
            continue
        if len(entries) >= limit:
            break

    output_result(ctx, entries)


def _list_server(
    ctx: typer.Context,
    *,
    status: str | None,
    limit: int,
    sort: str,
) -> None:
    """List jobs from the ComfyUI server (/api/jobs)."""
    client, _ = build_client(ctx)
    try:
        data = client.get_jobs(status=status or "", limit=limit, sort_by=sort)
    except Exception as exc:
        output_error(ctx, "JOBS_FAILED", f"Failed to fetch jobs: {exc}")
        return

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


# ---------------------------------------------------------------------------
# history show
# ---------------------------------------------------------------------------

@app.command("show")
def history_show(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
    run_id: str = typer.Argument(help="Run ID to show"),
):
    """Show details of a specific execution run.

    Tries the server first (jobs API, then history API), then falls back to
    the local history file.
    """

    # --- Try server-side first ---
    server_data = _show_from_server(ctx, run_id)
    if server_data is not None:
        fmt = get_output_format(ctx)
        if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
            output_result(ctx, server_data)
            return
        # Text mode
        console = Console()
        if isinstance(server_data, dict):
            for key, value in server_data.items():
                console.print(f"[bold]{key}:[/bold] {value}")
        else:
            console.print(server_data)
        return

    # --- Fall back to local file ---
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    server_id, workflow_id = _parse_skill_id(ctx, skill_id)

    hist_dir = _history_dir(base_dir, server_id, workflow_id)

    # Try exact match first, then prefix match
    record_path = hist_dir / f"{run_id}.json"
    if not record_path.exists():
        # Search for prefix match
        if hist_dir.exists():
            for f in hist_dir.iterdir():
                if f.name.startswith(run_id) and f.name.endswith(".json"):
                    record_path = f
                    break

    if not record_path.exists():
        output_error(ctx, "NOT_FOUND", f'Run "{run_id}" not found for {server_id}/{workflow_id}.')
        return

    with open(record_path, encoding="utf-8") as f:
        record = json.load(f)

    output_result(ctx, record)


def _show_from_server(ctx: typer.Context, run_id: str) -> Any | None:
    """Try to fetch a run from the server. Returns None on failure."""
    try:
        client, _ = build_client(ctx)
    except (SystemExit, typer.Exit):
        return None

    # Try jobs API first, then history
    try:
        data = client.get_job(run_id)
    except Exception:
        data = None

    if data is not None:
        return data

    try:
        data = client.get_history(run_id)
    except Exception:
        data = None

    return data
