"""comfyui-skill templates — discover workflow templates and subgraphs."""

from __future__ import annotations

import typer

from ..output import output_error, output_result
from ..utils import build_client

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def templates_list(
    ctx: typer.Context,
):
    """List workflow templates from custom nodes."""
    client, server_id = build_client(ctx)

    try:
        data = client.get_workflow_templates()
        output_result(ctx, {
            "server_id": server_id,
            "templates": data,
            "node_count": len(data),
        })
    except Exception as exc:
        output_error(ctx, "TEMPLATES_FAILED", f"Failed to fetch templates: {exc}")
        return


@app.command("subgraphs")
def templates_subgraphs(
    ctx: typer.Context,
):
    """List reusable subgraph components."""
    client, server_id = build_client(ctx)

    try:
        data = client.get_subgraphs()
        output_result(ctx, {
            "server_id": server_id,
            "subgraphs": data,
            "count": len(data),
        })
    except Exception as exc:
        output_error(ctx, "SUBGRAPHS_FAILED", f"Failed to fetch subgraphs: {exc}")
        return
