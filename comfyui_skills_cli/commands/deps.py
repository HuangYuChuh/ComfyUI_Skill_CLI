"""comfyui-skill deps check / install"""

from __future__ import annotations

import json
from typing import Any

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import output_error, output_event, output_result
from ..storage import get_workflow_data

app = typer.Typer()

# Known model loader node types and the input field that references a model file
MODEL_LOADER_MAP: dict[str, tuple[str, str]] = {
    "CheckpointLoaderSimple": ("ckpt_name", "checkpoints"),
    "CheckpointLoader": ("ckpt_name", "checkpoints"),
    "LoraLoader": ("lora_name", "loras"),
    "LoraLoaderModelOnly": ("lora_name", "loras"),
    "VAELoader": ("vae_name", "vae"),
    "ControlNetLoader": ("control_net_name", "controlnet"),
    "CLIPLoader": ("clip_name", "text_encoders"),
    "UNETLoader": ("unet_name", "diffusion_models"),
    "unCLIPCheckpointLoader": ("ckpt_name", "checkpoints"),
    "StyleModelLoader": ("style_model_name", "style_models"),
    "CLIPVisionLoader": ("clip_name", "clip_vision"),
    "UpscaleModelLoader": ("model_name", "upscale_models"),
    "PhotoMakerLoader": ("photomaker_model_name", "photomaker"),
}


@app.command("check")
def deps_check(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
):
    """Check if a skill's dependencies (custom nodes and models) are installed."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    if "/" in skill_id:
        server_id, workflow_id = skill_id.split("/", 1)
    else:
        server_id = ctx.obj.get("server") or get_default_server_id(config)
        workflow_id = skill_id

    server_config = get_server(config, server_id)
    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    workflow_data = get_workflow_data(base_dir, server_id, workflow_id)
    if not workflow_data:
        output_error(ctx, "SKILL_NOT_FOUND", f'Skill "{skill_id}" not found.')
        return

    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )

    # Check server is reachable
    health = client.check_health()
    if health.get("status") != "online":
        output_error(ctx, "SERVER_OFFLINE", f'Server "{server_id}" is offline.',
                     hint="Start ComfyUI first, then retry.")
        return

    # Get installed nodes
    try:
        object_info = client.get_object_info()
    except Exception as exc:
        output_error(ctx, "OBJECT_INFO_FAILED", f"Failed to query /object_info: {exc}")
        return
    installed_nodes = set(object_info.keys())

    # Extract required nodes from workflow
    required_nodes = set()
    for node in workflow_data.values():
        if isinstance(node, dict) and "class_type" in node:
            required_nodes.add(node["class_type"])

    # Find missing nodes
    missing_nodes = []
    for class_type in sorted(required_nodes - installed_nodes):
        missing_nodes.append({
            "class_type": class_type,
            "can_auto_install": False,
        })

    # Check models
    missing_models = _check_missing_models(client, workflow_data)

    is_ready = len(missing_nodes) == 0 and len(missing_models) == 0

    output_result(ctx, {
        "is_ready": is_ready,
        "missing_nodes": missing_nodes,
        "missing_models": missing_models,
        "total_nodes_required": len(required_nodes),
        "total_nodes_installed": len(required_nodes) - len(missing_nodes),
    })


@app.command("install")
def deps_install(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
    repos: str = typer.Option("[]", "--repos", "-r", help="JSON array of git repo URLs to install"),
):
    """Install missing custom node packages via ComfyUI Manager."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)

    if "/" in skill_id:
        server_id, workflow_id = skill_id.split("/", 1)
    else:
        server_id = ctx.obj.get("server") or get_default_server_id(config)
        workflow_id = skill_id

    server_config = get_server(config, server_id)
    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    # Parse repos
    try:
        repo_urls = json.loads(repos)
        if not isinstance(repo_urls, list):
            output_error(ctx, "INVALID_ARGS", "--repos must be a JSON array of URLs")
            return
    except json.JSONDecodeError:
        output_error(ctx, "INVALID_ARGS", "Invalid JSON for --repos")
        return

    if not repo_urls:
        output_error(ctx, "INVALID_ARGS", "No repo URLs provided. Use --repos '[\"https://github.com/...\"]'")
        return

    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )

    # Start manager queue
    if not client.manager_start_queue():
        output_error(ctx, "MANAGER_UNAVAILABLE",
                     "ComfyUI Manager is not available on this server.",
                     hint="Install ComfyUI-Manager first: https://github.com/ltdrdata/ComfyUI-Manager")
        return

    results = []
    needs_restart = False

    for repo_url in repo_urls:
        pkg_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        output_event(ctx, "installing", package=pkg_name, source=repo_url)

        install_result = client.manager_install_node(repo_url, pkg_name)

        if install_result.get("success"):
            # Wait for queue to finish
            success = client.manager_wait_for_queue(max_polls=60, interval=3.0)
            results.append({
                "package": pkg_name,
                "source": repo_url,
                "success": success,
                "method": "manager_queue",
                "message": "installed via Manager" if success else "Manager queue timed out",
            })
            if success:
                needs_restart = True
                output_event(ctx, "installed", package=pkg_name, success=True)
            else:
                output_event(ctx, "installed", package=pkg_name, success=False, message="queue timed out")
        else:
            error_msg = install_result.get("error", "unknown error")
            results.append({
                "package": pkg_name,
                "source": repo_url,
                "success": False,
                "message": error_msg,
            })
            output_event(ctx, "installed", package=pkg_name, success=False, message=error_msg)

    output_result(ctx, {
        "results": results,
        "needs_restart": needs_restart,
        "installed": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
    })


def _check_missing_models(client: ComfyUIClient, workflow_data: dict[str, Any]) -> list[dict[str, str]]:
    """Check for missing model files referenced in the workflow."""
    missing = []
    checked_folders: dict[str, set[str]] = {}

    for node_id, node in workflow_data.items():
        if not isinstance(node, dict):
            continue
        class_type = node.get("class_type", "")
        if class_type not in MODEL_LOADER_MAP:
            continue

        field_name, folder = MODEL_LOADER_MAP[class_type]
        inputs = node.get("inputs", {})
        model_filename = inputs.get(field_name)

        if not model_filename or not isinstance(model_filename, str):
            continue

        # Cache the model list per folder
        if folder not in checked_folders:
            try:
                models = client.get_models(folder)
                checked_folders[folder] = set(models) if isinstance(models, list) else set()
            except Exception:
                checked_folders[folder] = set()

        if model_filename not in checked_folders[folder]:
            missing.append({
                "filename": model_filename,
                "folder": folder,
                "loader_node": class_type,
                "node_id": str(node_id),
            })

    return missing
