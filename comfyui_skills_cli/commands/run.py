"""comfy-skills run / submit / status"""

from __future__ import annotations

import copy
import json
import os
import time
import uuid
from typing import Any

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import is_json_mode, output_error, output_event, output_result
from ..storage import get_schema, get_workflow_data

_POLL_INITIAL = 1.0
_POLL_MAX = 10.0
_POLL_FACTOR = 1.5


def run_cmd(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id or workflow_id"),
    args: str = typer.Option("{}", "--args", "-a", help="JSON parameters"),
):
    """Execute a skill (blocking — waits for completion)."""
    base_dir, server_id, workflow_id = _resolve_skill(ctx, skill_id)
    client, schema_data, workflow_data = _prepare(ctx, base_dir, server_id, workflow_id)

    input_args = _parse_args(ctx, args)
    parameters = _get_parameters(schema_data)

    # Inject parameters into workflow
    workflow = _inject_params(workflow_data, parameters, input_args)

    # Submit
    try:
        result = client.queue_prompt(workflow)
    except Exception as exc:
        output_error(ctx, "SUBMIT_FAILED", f"Failed to submit workflow: {exc}")
        return

    prompt_id = result.get("prompt_id", "")
    if is_json_mode(ctx):
        output_event("queued", prompt_id=prompt_id)

    # Poll until complete
    poll_interval = _POLL_INITIAL
    while True:
        history = client.get_history(prompt_id)
        if history:
            outputs = history.get("outputs", {})
            status_info = history.get("status", {})

            if status_info.get("completed", False) or outputs:
                images = _collect_outputs(outputs)
                output_result(ctx, {
                    "status": "success",
                    "prompt_id": prompt_id,
                    "outputs": images,
                })
                return

            if status_info.get("status_str") == "error":
                error_msg = _format_errors(history)
                output_error(ctx, "EXECUTION_FAILED", error_msg)
                return

        time.sleep(poll_interval)
        poll_interval = min(poll_interval * _POLL_FACTOR, _POLL_MAX)


def submit_cmd(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id or workflow_id"),
    args: str = typer.Option("{}", "--args", "-a", help="JSON parameters"),
):
    """Submit a skill for execution (non-blocking — returns immediately)."""
    base_dir, server_id, workflow_id = _resolve_skill(ctx, skill_id)
    client, schema_data, workflow_data = _prepare(ctx, base_dir, server_id, workflow_id)

    input_args = _parse_args(ctx, args)
    parameters = _get_parameters(schema_data)
    workflow = _inject_params(workflow_data, parameters, input_args)

    try:
        result = client.queue_prompt(workflow)
    except Exception as exc:
        output_error(ctx, "SUBMIT_FAILED", f"Failed to submit workflow: {exc}")
        return

    output_result(ctx, {
        "status": "submitted",
        "prompt_id": result.get("prompt_id", ""),
    })


def status_cmd(
    ctx: typer.Context,
    prompt_id: str = typer.Argument(help="Prompt ID from submit"),
):
    """Check execution status of a submitted workflow."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    client = _build_client(server_config)
    history = client.get_history(prompt_id)

    if history:
        status_info = history.get("status", {})
        outputs = history.get("outputs", {})
        if status_info.get("completed", False) or outputs:
            images = _collect_outputs(outputs)
            output_result(ctx, {"status": "success", "prompt_id": prompt_id, "outputs": images})
            return
        if status_info.get("status_str") == "error":
            output_result(ctx, {"status": "error", "prompt_id": prompt_id, "error": _format_errors(history)})
            return

    # Check queue
    queue = client.get_queue()
    for item in queue.get("queue_running", []):
        if item[1] == prompt_id:
            output_result(ctx, {"status": "running", "prompt_id": prompt_id})
            return
    for i, item in enumerate(queue.get("queue_pending", [])):
        if item[1] == prompt_id:
            output_result(ctx, {"status": "queued", "prompt_id": prompt_id, "position": i})
            return

    output_result(ctx, {"status": "not_found", "prompt_id": prompt_id})


# -- Helpers --

def _resolve_skill(ctx: typer.Context, skill_id: str) -> tuple[Any, str, str]:
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    if "/" in skill_id:
        server_id, workflow_id = skill_id.split("/", 1)
    else:
        config = load_config(base_dir)
        server_id = ctx.obj.get("server") or get_default_server_id(config)
        workflow_id = skill_id
    return base_dir, server_id, workflow_id


def _prepare(ctx: typer.Context, base_dir: Any, server_id: str, workflow_id: str):
    config = load_config(base_dir)
    server_config = get_server(config, server_id)
    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')

    schema_data = get_schema(base_dir, server_id, workflow_id)
    workflow_data = get_workflow_data(base_dir, server_id, workflow_id)
    if not workflow_data:
        output_error(ctx, "SKILL_NOT_FOUND", f'Skill "{server_id}/{workflow_id}" not found.')

    client = _build_client(server_config)
    return client, schema_data or {}, workflow_data


def _build_client(server_config: dict[str, Any]) -> ComfyUIClient:
    return ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
        comfy_api_key=server_config.get("comfy_api_key", ""),
    )


def _parse_args(ctx: typer.Context, args_str: str) -> dict[str, Any]:
    try:
        return json.loads(args_str)
    except json.JSONDecodeError as exc:
        output_error(ctx, "INVALID_ARGS", f"Invalid JSON in --args: {exc}")
        return {}


def _get_parameters(schema_data: dict[str, Any]) -> dict[str, Any]:
    parameters = dict(schema_data.get("parameters", {}))
    ui_parameters = schema_data.get("ui_parameters", {})
    if ui_parameters:
        for key, ui_param in ui_parameters.items():
            name = ui_param.get("name", key)
            if name not in parameters and ui_param.get("exposed", False):
                parameters[name] = ui_param
    return parameters


def _inject_params(
    workflow_data: dict[str, Any],
    parameters: dict[str, Any],
    args: dict[str, Any],
) -> dict[str, Any]:
    workflow = copy.deepcopy(workflow_data)
    for key, value in args.items():
        if key not in parameters:
            continue
        node_id = str(parameters[key].get("node_id", ""))
        field = parameters[key].get("field", "")
        if node_id in workflow and isinstance(workflow[node_id], dict) and "inputs" in workflow[node_id]:
            workflow[node_id]["inputs"][field] = value
    return workflow


def _collect_outputs(outputs: dict[str, Any]) -> list[dict[str, str]]:
    images = []
    for node_output in outputs.values():
        if not isinstance(node_output, dict):
            continue
        for img in node_output.get("images", []):
            images.append({
                "filename": img.get("filename", ""),
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            })
    return images


def _format_errors(history: dict[str, Any]) -> str:
    status_info = history.get("status", {})
    messages = status_info.get("messages", [])
    parts = []
    for msg in messages:
        if isinstance(msg, list) and len(msg) >= 2:
            parts.append(str(msg[1]))
    return "; ".join(parts) if parts else "Workflow execution failed"
