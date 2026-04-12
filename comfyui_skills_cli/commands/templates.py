"""comfyui-skill templates — discover workflow templates and subgraphs."""

from __future__ import annotations

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
def templates_list(
    ctx: typer.Context,
):
    """List workflow templates from custom nodes."""
    client, server_id = _build_client(ctx)

    try:
        data = client.get_workflow_templates()
        output_result(ctx, {
            "server_id": server_id,
            "templates": data,
            "node_count": len(data),
        })
    except Exception as exc:
        output_error(ctx, "TEMPLATES_FAILED", f"Failed to fetch templates: {exc}")


@app.command("subgraphs")
def templates_subgraphs(
    ctx: typer.Context,
):
    """List reusable subgraph components."""
    client, server_id = _build_client(ctx)

    try:
        data = client.get_subgraphs()
        output_result(ctx, {
            "server_id": server_id,
            "subgraphs": data,
            "count": len(data),
        })
    except Exception as exc:
        output_error(ctx, "SUBGRAPHS_FAILED", f"Failed to fetch subgraphs: {exc}")
