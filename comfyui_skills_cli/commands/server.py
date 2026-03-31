"""comfy-skills server list / status"""

from __future__ import annotations

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, get_servers, load_config
from ..output import output_error, output_result

app = typer.Typer()


@app.command("list")
def server_list(ctx: typer.Context):
    """List all configured servers."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    servers = get_servers(config)
    result = [
        {
            "id": s.get("id", ""),
            "name": s.get("name", ""),
            "url": s.get("url", ""),
            "enabled": s.get("enabled", True),
        }
        for s in servers
    ]
    output_result(ctx, result)


@app.command("status")
def server_status(
    ctx: typer.Context,
    server_id: str = typer.Argument("", help="Server ID (default: default server)"),
):
    """Check if a ComfyUI server is online."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    sid = server_id or ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, sid)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{sid}" not found.',
                     hint="Run `comfy-skills server list` to see configured servers.")
        return

    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )
    health = client.check_health()
    output_result(ctx, {
        "server_id": sid,
        "url": server_config.get("url", ""),
        **health,
    })
