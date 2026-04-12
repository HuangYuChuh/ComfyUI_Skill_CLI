"""comfyui-skill nodes — discover available ComfyUI nodes."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..output import get_output_format, OutputFormat, output_error, output_result
from ..utils import build_client

app = typer.Typer(no_args_is_help=True)


def _flatten_nodes(all_info: dict, category_filter: str = "") -> list[dict]:
    rows = []
    for class_type, info in all_info.items():
        cat = info.get("category") or ""
        display_name = info.get("display_name") or class_type
        if category_filter and category_filter.lower() != cat.lower():
            continue
        rows.append({
            "class_type": class_type,
            "display_name": display_name,
            "category": cat,
            "description": info.get("description") or "",
        })
    rows.sort(key=lambda r: (r["category"].lower(), r["display_name"].lower()))
    return rows


def _print_node_table(rows: list[dict]) -> None:
    console = Console()
    table = Table(show_lines=True)
    table.add_column("category")
    table.add_column("class_type")
    table.add_column("display_name")
    for r in rows:
        table.add_row(r["category"], r["class_type"], r["display_name"])
    console.print(table)


@app.command("list")
def nodes_list(
    ctx: typer.Context,
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
):
    """List all available node classes, grouped by category."""
    client, _ = build_client(ctx)
    try:
        all_info = client.get_object_info()
    except Exception as exc:
        output_error(ctx, "NODES_FAILED", f"Failed to fetch nodes: {exc}")
        return

    rows = _flatten_nodes(all_info, category or "")

    fmt = get_output_format(ctx)
    if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
        output_result(ctx, rows)
    else:
        _print_node_table(rows)


@app.command("info")
def nodes_info(
    ctx: typer.Context,
    node_class: str = typer.Argument(help="Node class name (e.g. KSampler)"),
):
    """Show full details of a single node class."""
    client, _ = build_client(ctx)
    try:
        info = client.get_object_info_node(node_class)
    except Exception as exc:
        output_error(ctx, "NODES_FAILED", f"Failed to fetch node info: {exc}")
        return

    if not info:
        output_error(ctx, "NODE_NOT_FOUND", f'Node class "{node_class}" not found.')

    fmt = get_output_format(ctx)
    if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
        output_result(ctx, info)
        return

    console = Console()
    console.print(f"[bold]display_name:[/bold] {info.get('display_name', node_class)}")
    console.print(f"[bold]category:[/bold] {info.get('category', '')}")
    console.print(f"[bold]description:[/bold] {info.get('description', '') or '-'}")

    inp = info.get("input", {})
    input_order = info.get("input_order", {})

    required = inp.get("required", {})
    if required:
        console.print("\n[bold]input_required:[/bold]")
        for name in input_order.get("required", list(required.keys())):
            spec = required.get(name, [])
            if not spec:
                continue
            type_info = spec[0]
            if isinstance(type_info, list):
                options = ", ".join(str(o) for o in type_info[:8])
                if len(type_info) > 8:
                    options += ", ..."
                console.print(f"  [cyan]{name}[/cyan] (COMBO): [{options}]")
            else:
                console.print(f"  [cyan]{name}[/cyan] ({type_info})")

    optional = inp.get("optional", {})
    if optional:
        console.print("\n[bold]input_optional:[/bold]")
        for name in input_order.get("optional", list(optional.keys())):
            spec = optional.get(name, [])
            if not spec:
                continue
            type_info = spec[0]
            if isinstance(type_info, list):
                options = ", ".join(str(o) for o in type_info[:8])
                if len(type_info) > 8:
                    options += ", ..."
                console.print(f"  [cyan]{name}[/cyan] (COMBO): [{options}]")
            else:
                console.print(f"  [cyan]{name}[/cyan] ({type_info})")

    output_names = info.get("output_name", [])
    output_types = info.get("output", [])
    if output_names:
        console.print("\n[bold]outputs:[/bold]")
        for i, name in enumerate(output_names):
            otype = output_types[i] if i < len(output_types) else ""
            console.print(f"  [cyan]{name}[/cyan] ({otype})")


@app.command("search")
def nodes_search(
    ctx: typer.Context,
    query: str = typer.Argument(help="Search query (substring match)"),
):
    """Fuzzy search across node names, display names, and categories."""
    client, _ = build_client(ctx)
    try:
        all_info = client.get_object_info()
    except Exception as exc:
        output_error(ctx, "NODES_FAILED", f"Failed to fetch nodes: {exc}")
        return

    q = query.lower()
    rows = []
    for class_type, info in all_info.items():
        display_name = info.get("display_name") or class_type
        cat = info.get("category") or ""
        if q in class_type.lower() or q in display_name.lower() or q in cat.lower():
            rows.append({
                "class_type": class_type,
                "display_name": display_name,
                "category": cat,
                "description": info.get("description") or "",
            })
    rows.sort(key=lambda r: (r["category"].lower(), r["display_name"].lower()))

    fmt = get_output_format(ctx)
    if fmt in (OutputFormat.JSON, OutputFormat.STREAM_JSON):
        output_result(ctx, rows)
    else:
        _print_node_table(rows)
