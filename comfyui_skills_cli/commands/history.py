"""comfyui-skill history list / show — execution history management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from ..config import get_base_dir, get_default_server_id, load_config
from ..output import output_error, output_result

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


@app.command("list")
def history_list(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max entries to return"),
):
    """List execution history for a skill."""
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


@app.command("show")
def history_show(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
    run_id: str = typer.Argument(help="Run ID to show"),
):
    """Show details of a specific execution run."""
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
