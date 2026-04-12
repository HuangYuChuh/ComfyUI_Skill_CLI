"""comfy-skills server list / status / add / enable / disable / remove"""

from __future__ import annotations

import re

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, get_servers, load_config, save_config
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


def _fmt_bytes(n: int) -> str:
    """Format bytes as human-readable GB."""
    return f"{n / (1024 ** 3):.1f} GB"


@app.command("stats")
def server_stats(
    ctx: typer.Context,
    server_id: str = typer.Argument("", help="Server ID (default: default server)"),
    all_servers: bool = typer.Option(False, "--all", help="Query all enabled servers"),
):
    """Show detailed system stats (RAM, VRAM, versions) for a ComfyUI server."""
    from ..output import get_output_format, is_machine_mode, OutputFormat
    from rich.console import Console

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    if all_servers:
        servers_list = [s for s in get_servers(config) if s.get("enabled", True)]
    else:
        sid = server_id or ctx.obj.get("server") or get_default_server_id(config)
        server_config = get_server(config, sid)
        if not server_config:
            output_error(ctx, "SERVER_NOT_FOUND", f'Server "{sid}" not found.',
                         hint="Run `comfy-skills server list` to see configured servers.")
            return
        servers_list = [server_config]

    results = []
    for srv in servers_list:
        sid = srv.get("id", "")
        client = ComfyUIClient(
            server_url=srv.get("url", "http://127.0.0.1:8188"),
            auth=srv.get("auth", ""),
        )
        try:
            stats = client.get_system_stats()
            results.append({"server_id": sid, **stats})
        except Exception as exc:
            results.append({"server_id": sid, "error": str(exc)})

    if is_machine_mode(ctx):
        output_result(ctx, results if all_servers else results[0])
    else:
        console = Console()
        for entry in results:
            if "error" in entry:
                console.print(f"[bold]{entry['server_id']}:[/bold] [red]offline[/red] — {entry['error']}")
                continue
            system = entry.get("system", {})
            devices = entry.get("devices", [])
            console.print(f"[bold]Server:[/bold] {entry['server_id']}")
            console.print(f"  OS: {system.get('os', '?')}  |  ComfyUI: {system.get('comfyui_version', '?')}  |  Python: {system.get('python_version', '?')}  |  PyTorch: {system.get('pytorch_version', '?')}")
            console.print(f"  RAM: {_fmt_bytes(system.get('ram_total', 0))} total, {_fmt_bytes(system.get('ram_free', 0))} free")
            for dev in devices:
                console.print(f"  Device [{dev.get('name', '?')}]: VRAM {_fmt_bytes(dev.get('vram_total', 0))} total, {_fmt_bytes(dev.get('vram_free', 0))} free")
            console.print()


_INVALID_ID_PATTERN = re.compile(r"[/\\.\s]")


@app.command("add")
def server_add(
    ctx: typer.Context,
    server_id: str = typer.Option(..., "--id", help="Unique server ID"),
    url: str = typer.Option(..., "--url", help="ComfyUI server URL"),
    name: str = typer.Option("", "--name", help="Display name (default: same as id)"),
    output_dir: str = typer.Option("./outputs", "--output-dir", help="Image output directory"),
    auth: str = typer.Option("", "--auth", help="Bearer token for authentication"),
    comfy_api_key: str = typer.Option("", "--api-key", help="ComfyUI API key for cloud nodes"),
):
    """Add a new ComfyUI server."""
    if _INVALID_ID_PATTERN.search(server_id) or not server_id:
        output_error(ctx, "INVALID_ID",
                     "Server ID must not contain spaces, slashes, backslashes, or dots.")
        return

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    if get_server(config, server_id):
        output_error(ctx, "ALREADY_EXISTS", f'Server "{server_id}" already exists.')
        return

    new_server: dict = {
        "id": server_id,
        "name": name or server_id,
        "url": url.rstrip("/"),
        "enabled": True,
        "output_dir": output_dir,
    }
    if auth:
        new_server["auth"] = auth
    if comfy_api_key:
        new_server["comfy_api_key"] = comfy_api_key

    config.setdefault("servers", []).append(new_server)
    if len(config["servers"]) == 1:
        config["default_server"] = server_id

    save_config(base_dir, config)
    output_result(ctx, {"server_id": server_id, "added": True, **new_server})


@app.command("enable")
def server_enable(
    ctx: typer.Context,
    server_id: str = typer.Argument(help="Server ID to enable"),
):
    """Enable a server."""
    _toggle_server(ctx, server_id, enabled=True)


@app.command("disable")
def server_disable(
    ctx: typer.Context,
    server_id: str = typer.Argument(help="Server ID to disable"),
):
    """Disable a server."""
    _toggle_server(ctx, server_id, enabled=False)


@app.command("remove")
def server_remove(
    ctx: typer.Context,
    server_id: str = typer.Argument(help="Server ID to remove"),
):
    """Remove a server from config (does not delete workflow data)."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    servers = config.get("servers", [])
    new_servers = [s for s in servers if s.get("id") != server_id]

    if len(new_servers) == len(servers):
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    config["servers"] = new_servers
    if config.get("default_server") == server_id:
        config["default_server"] = new_servers[0]["id"] if new_servers else ""

    save_config(base_dir, config)
    output_result(ctx, {"server_id": server_id, "removed": True})


@app.command("features")
def server_features(
    ctx: typer.Context,
    server_id: str = typer.Argument("", help="Server ID (default: default server)"),
):
    """Show server feature flags and capabilities."""
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
    try:
        features = client.get_features()
        output_result(ctx, {"server_id": sid, "features": features})
    except Exception as exc:
        output_error(ctx, "SERVER_ERROR", f"Failed to fetch features: {exc}")
        return


def _toggle_server(ctx: typer.Context, server_id: str, enabled: bool) -> None:
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    for s in config.get("servers", []):
        if s.get("id") == server_id:
            s["enabled"] = enabled
            save_config(base_dir, config)
            output_result(ctx, {"server_id": server_id, "enabled": enabled})
            return

    output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
