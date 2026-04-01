"""Unified output formatting — the only place that handles text / JSON / stream-JSON."""

from __future__ import annotations

import json
import sys
from enum import Enum
from typing import Any

import typer
from rich.console import Console
from rich.table import Table


class OutputFormat(str, Enum):
    TEXT = "text"                # Rich tables, progress bars (human)
    JSON = "json"               # Single JSON result at end (agent, one-shot)
    STREAM_JSON = "stream-json" # NDJSON events in real time (agent, streaming)


def get_output_format(ctx: typer.Context) -> OutputFormat:
    if ctx.obj:
        fmt = ctx.obj.get("output_format", "")
        if fmt:
            return OutputFormat(fmt)
        if ctx.obj.get("json"):
            return OutputFormat.JSON
    if not sys.stdout.isatty():
        return OutputFormat.JSON
    return OutputFormat.TEXT


def is_machine_mode(ctx: typer.Context) -> bool:
    return get_output_format(ctx) in (OutputFormat.JSON, OutputFormat.STREAM_JSON)


def output_result(ctx: typer.Context, data: Any) -> None:
    fmt = get_output_format(ctx)
    if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
        indent = 2 if sys.stdout.isatty() else None
        json.dump(data, sys.stdout, ensure_ascii=False, indent=indent, default=str)
        sys.stdout.write("\n")
    else:
        _print_rich(data)


def output_error(ctx: typer.Context, code: str, message: str, hint: str = "") -> None:
    if is_machine_mode(ctx):
        err: dict[str, Any] = {"error": {"code": code, "message": message}}
        if hint:
            err["error"]["hint"] = hint
        json.dump(err, sys.stderr, ensure_ascii=False)
        sys.stderr.write("\n")
    else:
        console = Console(stderr=True)
        console.print(f"[red bold]Error:[/red bold] {message}")
        if hint:
            console.print(f"[dim]Hint: {hint}[/dim]")
    raise typer.Exit(code=1)


def output_event(ctx: typer.Context, event_type: str, **data: Any) -> None:
    """Emit a single NDJSON event line. Only outputs in stream-json mode."""
    fmt = get_output_format(ctx)
    if fmt == OutputFormat.STREAM_JSON:
        json.dump({"event": event_type, **data}, sys.stdout, ensure_ascii=False, default=str)
        sys.stdout.write("\n")
        sys.stdout.flush()


def _format_cell(key: str, value: Any) -> str:
    """Format a cell value for Rich table display."""
    if key == "parameters" and isinstance(value, dict):
        parts = []
        for name, meta in value.items():
            req = "*" if (isinstance(meta, dict) and meta.get("required")) else ""
            parts.append(f"{req}{name}")
        return ", ".join(parts) if parts else "-"
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _print_rich(data: Any) -> None:
    console = Console()
    if isinstance(data, list) and data and isinstance(data[0], dict):
        table = Table(show_lines=True)
        keys = list(data[0].keys())
        for key in keys:
            table.add_column(key)
        for item in data:
            table.add_row(*[_format_cell(k, item.get(k, "")) for k in keys])
        console.print(table)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                console.print(f"[bold]{key}:[/bold]")
                for k, v in value.items():
                    if isinstance(v, dict):
                        req = " [red](required)[/red]" if v.get("required") else ""
                        desc = v.get("description", "")
                        vtype = v.get("type", "")
                        console.print(f"  [cyan]{k}[/cyan] ({vtype}){req}: {desc}")
                    else:
                        console.print(f"  [cyan]{k}:[/cyan] {v}")
            else:
                console.print(f"[bold]{key}:[/bold] {value}")
    else:
        console.print(data)
