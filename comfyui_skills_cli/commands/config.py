"""comfyui-skill config export / import — configuration transfer."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

import typer

from ..config import get_base_dir, get_servers, load_config, save_config
from ..output import output_error, output_event, output_result

app = typer.Typer()


_DEFAULT_EXPORT_NAME = "comfyui-skill-export.json"


@app.command("export")
def config_export(
    ctx: typer.Context,
    output: str = typer.Option("", "--output", "-o", help="Output file or directory (default: ./comfyui-skill-export.json)"),
    portable_only: bool = typer.Option(False, "--portable-only", help="Exclude server URLs and auth"),
):
    """Export config and workflows as a portable bundle."""
    if not output:
        output = os.path.join(os.getcwd(), _DEFAULT_EXPORT_NAME)
    elif os.path.isdir(output):
        output = os.path.join(output, _DEFAULT_EXPORT_NAME)
    else:
        output = os.path.abspath(output)

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    bundle: dict[str, Any] = {
        "version": 1,
        "config": {},
        "workflows": {},
    }

    # Config
    servers = []
    for s in get_servers(config):
        server_entry: dict[str, Any] = {
            "id": s.get("id", ""),
            "name": s.get("name", ""),
            "enabled": s.get("enabled", True),
            "output_dir": s.get("output_dir", "./outputs"),
        }
        if not portable_only:
            server_entry["url"] = s.get("url", "")
            if s.get("auth"):
                server_entry["auth"] = s["auth"]
            if s.get("comfy_api_key"):
                server_entry["comfy_api_key"] = s["comfy_api_key"]
        servers.append(server_entry)

    bundle["config"] = {
        "servers": servers,
        "default_server": config.get("default_server", ""),
    }

    # Workflows
    data_dir = base_dir / "data"
    if data_dir.exists():
        for server_dir in sorted(data_dir.iterdir()):
            if not server_dir.is_dir():
                continue
            server_id = server_dir.name
            for workflow_dir in sorted(server_dir.iterdir()):
                if not workflow_dir.is_dir():
                    continue
                workflow_id = workflow_dir.name
                entry: dict[str, Any] = {}

                workflow_path = workflow_dir / "workflow.json"
                schema_path = workflow_dir / "schema.json"

                if workflow_path.exists():
                    with open(workflow_path, encoding="utf-8") as f:
                        entry["workflow"] = json.load(f)
                if schema_path.exists():
                    with open(schema_path, encoding="utf-8") as f:
                        entry["schema"] = json.load(f)

                if entry:
                    bundle["workflows"][f"{server_id}/{workflow_id}"] = entry

    with open(output, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    output_result(ctx, {
        "exported": output,
        "servers": len(servers),
        "workflows": len(bundle["workflows"]),
    })


@app.command("import")
def config_import(
    ctx: typer.Context,
    input_path: str = typer.Argument(help="Path to bundle JSON file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
    apply_environment: bool = typer.Option(False, "--apply-environment",
                                           help="Also apply server URLs and default_server from bundle"),
    no_overwrite: bool = typer.Option(False, "--no-overwrite", help="Skip existing workflows"),
):
    """Import config and workflows from a bundle."""
    if not os.path.isfile(input_path):
        output_error(ctx, "FILE_NOT_FOUND", f'Bundle file not found: "{input_path}"')
        return

    with open(input_path, encoding="utf-8") as f:
        bundle = json.load(f)

    if not isinstance(bundle, dict) or "config" not in bundle:
        output_error(ctx, "INVALID_BUNDLE", "Invalid bundle format.")
        return

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    bundle_config = bundle.get("config", {})
    bundle_workflows = bundle.get("workflows", {})
    bundle_servers = bundle_config.get("servers", [])

    # Preview
    preview: dict[str, Any] = {
        "servers_in_bundle": len(bundle_servers),
        "workflows_in_bundle": len(bundle_workflows),
        "actions": [],
    }

    # Server merge plan
    existing_ids = {s.get("id") for s in get_servers(config)}
    for bs in bundle_servers:
        sid = bs.get("id", "")
        if sid in existing_ids:
            preview["actions"].append({"type": "server", "id": sid, "action": "merge"})
        else:
            preview["actions"].append({"type": "server", "id": sid, "action": "add"})

    # Workflow plan
    for wf_key in bundle_workflows:
        parts = wf_key.split("/", 1)
        if len(parts) != 2:
            continue
        server_id, workflow_id = parts
        workflow_dir = base_dir / "data" / server_id / workflow_id
        if workflow_dir.exists():
            if no_overwrite:
                preview["actions"].append({"type": "workflow", "id": wf_key, "action": "skip"})
            else:
                preview["actions"].append({"type": "workflow", "id": wf_key, "action": "overwrite"})
        else:
            preview["actions"].append({"type": "workflow", "id": wf_key, "action": "create"})

    if dry_run:
        output_result(ctx, preview)
        return

    # Apply servers
    for bs in bundle_servers:
        sid = bs.get("id", "")
        existing = None
        for s in config.get("servers", []):
            if s.get("id") == sid:
                existing = s
                break

        if existing:
            # Merge: update name, enabled; optionally URL
            existing["name"] = bs.get("name", existing.get("name", ""))
            existing["enabled"] = bs.get("enabled", existing.get("enabled", True))
            if apply_environment:
                if "url" in bs:
                    existing["url"] = bs["url"]
                if "auth" in bs:
                    existing["auth"] = bs["auth"]
                if "comfy_api_key" in bs:
                    existing["comfy_api_key"] = bs["comfy_api_key"]
        else:
            config.setdefault("servers", []).append(bs)

    if apply_environment and "default_server" in bundle_config:
        config["default_server"] = bundle_config["default_server"]

    save_config(base_dir, config)

    # Apply workflows
    created = 0
    overwritten = 0
    skipped = 0
    for wf_key, wf_data in bundle_workflows.items():
        parts = wf_key.split("/", 1)
        if len(parts) != 2:
            continue
        server_id, workflow_id = parts
        workflow_dir = base_dir / "data" / server_id / workflow_id

        if workflow_dir.exists() and no_overwrite:
            skipped += 1
            continue

        workflow_dir.mkdir(parents=True, exist_ok=True)
        existed = (workflow_dir / "workflow.json").exists()

        if "workflow" in wf_data:
            with open(workflow_dir / "workflow.json", "w", encoding="utf-8") as f:
                json.dump(wf_data["workflow"], f, ensure_ascii=False, indent=2)
        if "schema" in wf_data:
            with open(workflow_dir / "schema.json", "w", encoding="utf-8") as f:
                json.dump(wf_data["schema"], f, ensure_ascii=False, indent=2)

        if existed:
            overwritten += 1
        else:
            created += 1

        output_event(ctx, "imported", workflow=wf_key)

    output_result(ctx, {
        "created": created,
        "overwritten": overwritten,
        "skipped": skipped,
        "servers_updated": len(bundle_servers),
    })
