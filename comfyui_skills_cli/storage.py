"""Read workflow and schema data from the data/ directory."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _is_under(child: Path, parent: Path) -> bool:
    """Check if *child* lives inside *parent* — works on both Windows and POSIX."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _safe_path(base_dir: Path, server_id: str, workflow_id: str) -> Path:
    """Construct and validate a workflow directory path. Raises ValueError on traversal."""
    target = (base_dir / "data" / server_id / workflow_id).resolve()
    if not _is_under(target, base_dir / "data"):
        raise ValueError(f"Invalid path: {server_id}/{workflow_id}")
    return target


def list_workflows(base_dir: Path, server_id: str) -> list[dict[str, Any]]:
    data_dir = (base_dir / "data" / server_id).resolve()
    if not _is_under(data_dir, base_dir / "data"):
        return []
    if not data_dir.exists():
        return []

    workflows = []
    for workflow_dir in sorted(data_dir.iterdir()):
        if not workflow_dir.is_dir():
            continue
        schema_path = workflow_dir / "schema.json"
        if not schema_path.exists():
            continue
        schema = _load_json(schema_path)
        params = _summarize_params(schema)
        workflows.append({
            "workflow_id": workflow_dir.name,
            "server_id": server_id,
            "description": schema.get("description", ""),
            "enabled": schema.get("enabled", True),
            "param_count": len(params),
            "parameters": params,
        })
    return workflows


def get_workflow_detail(base_dir: Path, server_id: str, workflow_id: str) -> dict[str, Any] | None:
    try:
        workflow_dir = _safe_path(base_dir, server_id, workflow_id)
    except ValueError:
        return None
    if not workflow_dir.is_dir():
        return None

    schema = _load_json(workflow_dir / "schema.json") if (workflow_dir / "schema.json").exists() else {}
    workflow_data = _load_json(workflow_dir / "workflow.json") if (workflow_dir / "workflow.json").exists() else {}

    parameters = schema.get("parameters", {})
    ui_parameters = schema.get("ui_parameters", {})
    merged = _merge_parameters(parameters, ui_parameters)

    return {
        "workflow_id": workflow_id,
        "server_id": server_id,
        "description": schema.get("description", ""),
        "enabled": schema.get("enabled", True),
        "parameters": merged,
        "workflow_data": workflow_data,
    }


def get_workflow_data(base_dir: Path, server_id: str, workflow_id: str) -> dict[str, Any] | None:
    try:
        path = _safe_path(base_dir, server_id, workflow_id) / "workflow.json"
    except ValueError:
        return None
    if not path.exists():
        return None
    return _load_json(path)


def get_schema(base_dir: Path, server_id: str, workflow_id: str) -> dict[str, Any] | None:
    try:
        path = _safe_path(base_dir, server_id, workflow_id) / "schema.json"
    except ValueError:
        return None
        return None
    return _load_json(path)


def _load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _summarize_params(schema: dict[str, Any]) -> dict[str, Any]:
    parameters = schema.get("parameters", {})
    ui_parameters = schema.get("ui_parameters", {})
    merged = _merge_parameters(parameters, ui_parameters)
    return {
        name: {
            "type": p.get("type", "string"),
            "required": p.get("required", False),
            "description": p.get("description", ""),
        }
        for name, p in merged.items()
        if p.get("exposed", True)
    }


def _merge_parameters(
    parameters: dict[str, Any],
    ui_parameters: dict[str, Any],
) -> dict[str, Any]:
    if not ui_parameters:
        return parameters
    merged = dict(parameters)
    for key, ui_param in ui_parameters.items():
        name = ui_param.get("name", key)
        if name in merged:
            for field in ("type", "required", "description", "default"):
                if field in ui_param and ui_param[field]:
                    merged[name][field] = ui_param[field]
        elif ui_param.get("exposed", False):
            merged[name] = ui_param
    return merged
