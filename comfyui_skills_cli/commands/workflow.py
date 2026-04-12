"""comfyui-skill workflow — import, enable, disable, delete workflows."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import output_error, output_event, output_result
from ..storage import _safe_path

app = typer.Typer()


# ── Format detection ──────────────────────────────────────────────


def _is_editor_workflow(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and isinstance(data.get("nodes"), list)
        and isinstance(data.get("links"), list)
    )


def _is_api_workflow(data: Any) -> bool:
    if not isinstance(data, dict) or not data:
        return False
    if _is_editor_workflow(data):
        return False
    for key, value in data.items():
        if not isinstance(key, str) or not key.strip():
            return False
        if not isinstance(value, dict) or "class_type" not in value:
            return False
    return True


# ── Schema generation ─────────────────────────────────────────────


_AUTO_EXPOSE_FIELDS: dict[str, dict[str, Any]] = {
    "text": {"exposed": True, "required": True, "description": "Text prompt"},
    "prompt": {"exposed": True, "required": True, "description": "Text prompt"},
    "seed": {"exposed": True, "required": False, "description": "Random seed"},
    "width": {"exposed": True, "required": False, "description": "Image width"},
    "height": {"exposed": True, "required": False, "description": "Image height"},
    "batch_size": {"exposed": True, "required": False, "description": "Batch size"},
    "size": {"exposed": True, "required": False, "description": "Image size"},
    "num": {"exposed": True, "required": False, "description": "Number of images"},
    "steps": {"exposed": True, "required": False, "description": "Generation steps"},
    "filename_prefix": {"exposed": True, "required": False, "description": "Output file prefix"},
}

_MEDIA_TYPE_FIELDS: dict[str, dict[str, dict[str, Any]]] = {
    "audio": {
        "tags": {"exposed": True, "required": True, "description": "Music style/genre tags"},
        "lyrics": {"exposed": True, "required": False, "description": "Song lyrics"},
        "bpm": {"exposed": True, "required": False, "description": "Beats per minute"},
        "duration": {"exposed": True, "required": False, "description": "Audio duration"},
        "seconds": {"exposed": True, "required": False, "description": "Duration in seconds"},
        "language": {"exposed": True, "required": False, "description": "Language code"},
        "keyscale": {"exposed": True, "required": False, "description": "Musical key and scale"},
        "cfg_scale": {"exposed": True, "required": False, "description": "Classifier-free guidance scale"},
        "temperature": {"exposed": True, "required": False, "description": "Sampling temperature"},
    },
}

_LOAD_IMAGE_CLASSES = {"LoadImage", "LoadImageMask"}


def _get_type_guess(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    return "string"


def _extract_schema(workflow_data: dict[str, Any], media_type: str = "image") -> dict[str, dict[str, Any]]:
    """Extract parameters from API-format workflow and build schema.

    *media_type* selects additional field-exposure rules beyond the base
    set.  ``"image"`` (default) uses only the generic rules.
    ``"audio"`` adds audio-specific fields like tags, lyrics, bpm, etc.
    """
    expose_fields = dict(_AUTO_EXPOSE_FIELDS)
    if media_type in _MEDIA_TYPE_FIELDS:
        expose_fields.update(_MEDIA_TYPE_FIELDS[media_type])

    raw_params: list[dict[str, Any]] = []

    for node_id, node in workflow_data.items():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue

        class_type = (node.get("class_type") or "").strip()
        for field, value in inputs.items():
            # Skip linked inputs (arrays = connections)
            if isinstance(value, list):
                continue

            # Determine exposure
            if class_type in _LOAD_IMAGE_CLASSES and field == "image":
                exposed, required = True, True
                description = "Upload an image"
                field_type = "image"
            elif field in expose_fields:
                info = expose_fields[field]
                exposed = info["exposed"]
                required = info["required"]
                description = info["description"]
                field_type = _get_type_guess(value)
            else:
                exposed = False
                required = False
                description = ""
                field_type = _get_type_guess(value)

            if not exposed:
                continue

            raw_params.append({
                "node_id": str(node_id),
                "field": field,
                "type": field_type,
                "required": required,
                "description": description,
                "default": value,
                "class_type": class_type,
            })

    # Assign unique names
    field_counts: dict[str, int] = {}
    for p in raw_params:
        field_counts[p["field"]] = field_counts.get(p["field"], 0) + 1

    parameters: dict[str, dict[str, Any]] = {}
    for p in raw_params:
        name = _friendly_name(p["field"])
        if field_counts[p["field"]] > 1:
            # Disambiguate with node title or id
            title = _get_node_title(workflow_data.get(p["node_id"], {}))
            suffix = _normalize_title(title) if title else p["node_id"]
            name = f"{name}_{suffix}"

        # Ensure unique
        base_name = name
        counter = 2
        while name in parameters:
            name = f"{base_name}_{counter}"
            counter += 1

        parameters[name] = {
            "node_id": p["node_id"],
            "field": p["field"],
            "required": p["required"],
            "type": p["type"],
            "description": p["description"],
        }

    return parameters


def _friendly_name(field: str) -> str:
    return {"text": "prompt"}.get(field, field)


def _get_node_title(node: dict[str, Any]) -> str:
    meta = node.get("_meta")
    if isinstance(meta, dict):
        title = meta.get("title", "")
        if isinstance(title, str) and title.strip():
            return title.strip()
    return ""


def _normalize_title(title: str) -> str:
    normalized = re.sub(r"[^\w]+", "_", title.strip(), flags=re.UNICODE)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_").lower()


def _suggest_workflow_id(data: dict[str, Any], filename: str = "") -> str:
    def normalize(value: Any) -> str:
        if not isinstance(value, str):
            return ""
        n = re.sub(r"[./\\]+", "-", value.strip())
        n = re.sub(r"[^\w-]+", "-", n, flags=re.UNICODE)
        n = re.sub(r"-+", "-", n)
        return n.strip("-_")

    base_filename = re.sub(r"\.[^.]+$", "", filename).strip() if filename else ""
    candidates = [
        data.get("workflow_name"),
        data.get("name"),
        data.get("title"),
        base_filename,
    ]
    for c in candidates:
        n = normalize(c)
        if n:
            return n
    return "workflow"


# ── Editor → API conversion ──────────────────────────────────────


def _convert_editor_to_api(
    editor_data: dict[str, Any], object_info: dict[str, Any]
) -> dict[str, Any]:
    """Convert editor-format workflow to API format.

    Ported from ui/workflow_format.py EditorWorkflowConverter.
    """
    nodes = editor_data.get("nodes", [])
    links = editor_data.get("links", [])

    node_by_id: dict[int, dict[str, Any]] = {}
    for node in nodes:
        if isinstance(node, dict) and node.get("id") is not None:
            node_by_id[int(node["id"])] = node

    # Build link map: (target_node_id, target_slot) → (source_node_id_str, source_slot)
    link_map: dict[tuple[int, int], tuple[str, int]] = {}
    for link in links:
        if not isinstance(link, list) or len(link) < 5:
            continue
        source = _resolve_reroute(int(link[1]), int(link[2]), node_by_id, links)
        if source is not None:
            link_map[(int(link[3]), int(link[4]))] = source

    api_workflow: dict[str, Any] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        class_type = (node.get("type") or "").strip()
        if node_id is None or not class_type or class_type in {"Reroute", "Note"}:
            continue

        node_info = object_info.get(class_type)
        if not isinstance(node_info, dict):
            continue

        title = (node.get("title") or class_type).strip()
        inputs = _convert_node_inputs(node, class_type, node_info, link_map)
        api_workflow[str(node_id)] = {
            "inputs": inputs,
            "class_type": class_type,
            "_meta": {"title": title},
        }

    return api_workflow


def _resolve_reroute(
    source_id: int, source_slot: int,
    node_by_id: dict[int, dict[str, Any]], links: list[Any],
) -> tuple[str, int] | None:
    node = node_by_id.get(source_id)
    if not isinstance(node, dict):
        return (str(source_id), source_slot)
    if (node.get("type") or "").strip() != "Reroute":
        return (str(source_id), source_slot)

    input_slots = node.get("inputs", [])
    if not isinstance(input_slots, list) or not input_slots:
        return None
    incoming_link_id = input_slots[0].get("link") if isinstance(input_slots[0], dict) else None
    if incoming_link_id is None:
        return None

    for link in links:
        if isinstance(link, list) and len(link) >= 5 and int(link[0]) == int(incoming_link_id):
            return _resolve_reroute(int(link[1]), int(link[2]), node_by_id, links)
    return None


def _convert_node_inputs(
    node: dict[str, Any], class_type: str,
    node_info: dict[str, Any], link_map: dict[tuple[int, int], tuple[str, int]],
) -> dict[str, Any]:
    node_id = int(node["id"])
    input_slots = node.get("inputs", [])
    if not isinstance(input_slots, list):
        input_slots = []
    widget_values = node.get("widgets_values", [])
    if not isinstance(widget_values, list):
        widget_values = []

    converted: dict[str, Any] = {}
    connected_names: set[str] = set()

    # Connected inputs
    for slot_idx, slot in enumerate(input_slots):
        if not isinstance(slot, dict):
            continue
        slot_name = (slot.get("name") or "").strip()
        if not slot_name:
            continue
        link_tuple = link_map.get((node_id, slot_idx))
        if link_tuple is None:
            continue
        converted[slot_name] = [link_tuple[0], link_tuple[1]]
        connected_names.add(slot_name)

    # Widget values
    widget_field_names = _get_ordered_input_names(node_info)
    widget_field_names = [n for n in widget_field_names if n not in connected_names]

    control_fields = _get_control_after_generate_fields(node_info)
    widget_idx = 0
    for field_name in widget_field_names:
        if widget_idx >= len(widget_values):
            break
        converted[field_name] = widget_values[widget_idx]
        widget_idx += 1
        if field_name in control_fields and widget_idx < len(widget_values):
            val = widget_values[widget_idx]
            if isinstance(val, str) and val.lower() in {"fixed", "increment", "decrement", "randomize"}:
                widget_idx += 1

    return converted


def _get_ordered_input_names(node_info: dict[str, Any]) -> list[str]:
    ordered: list[str] = []
    input_order = node_info.get("input_order")
    if isinstance(input_order, dict):
        for section in ("required", "optional"):
            items = input_order.get(section)
            if isinstance(items, list):
                ordered.extend(str(i).strip() for i in items if str(i).strip())
    if ordered:
        return ordered

    input_section = node_info.get("input")
    if isinstance(input_section, dict):
        for section in ("required", "optional"):
            s = input_section.get(section)
            if isinstance(s, dict):
                ordered.extend(s.keys())
    return ordered


def _get_control_after_generate_fields(node_info: dict[str, Any]) -> set[str]:
    fields: set[str] = set()

    def visit(section: Any) -> None:
        if not isinstance(section, dict):
            return
        for name, defn in section.items():
            if isinstance(defn, list) and len(defn) >= 2 and isinstance(defn[1], dict):
                if defn[1].get("control_after_generate"):
                    fields.add(name)

    inp = node_info.get("input")
    if isinstance(inp, dict):
        visit(inp.get("required"))
        visit(inp.get("optional"))
    visit(node_info.get("required"))
    visit(node_info.get("optional"))
    return fields


# ── Commands ──────────────────────────────────────────────────────


@app.command("import")
def workflow_import(
    ctx: typer.Context,
    json_path: str = typer.Argument(None, help="Path to workflow JSON file (omit when using --from-server)"),
    name: str = typer.Option("", "--name", "-n", help="Workflow ID (default: derived from filename)"),
    media_type: str = typer.Option("image", "--type", "-t", help="Media type preset for parameter detection: image (default), audio"),
    from_server: bool = typer.Option(False, "--from-server", help="Import from ComfyUI server userdata"),
    preview: bool = typer.Option(False, "--preview", help="Preview only, don't import"),
    check_deps: bool = typer.Option(False, "--check-deps", help="Check dependencies after import"),
):
    """Import a workflow from local JSON or ComfyUI server.

    Use --type to select a parameter detection preset. The default (image)
    detects generic fields like seed, steps, and prompt. Use --type audio
    to also detect audio-specific fields like tags, lyrics, bpm, duration,
    keyscale, language, cfg_scale, and temperature.
    """
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    if from_server:
        _import_from_server(ctx, base_dir, server_id, server_config, name, preview, check_deps, media_type)
    elif json_path:
        _import_from_file(ctx, base_dir, server_id, server_config, json_path, name, preview, check_deps, media_type)
    else:
        output_error(ctx, "INVALID_ARGS", "Provide a JSON file path or use --from-server.")


def _import_from_file(
    ctx: typer.Context, base_dir: Path, server_id: str,
    server_config: dict[str, Any], json_path: str, name: str,
    preview: bool, check_deps: bool, media_type: str = "image",
) -> None:
    if not os.path.isfile(json_path):
        output_error(ctx, "FILE_NOT_FOUND", f'File not found: "{json_path}"')
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    filename = os.path.basename(json_path)
    workflow_id = name or _suggest_workflow_id(data, filename)

    # Detect format and convert if needed
    if _is_api_workflow(data):
        api_data = data
        format_detected = "api"
    elif _is_editor_workflow(data):
        format_detected = "editor"
        output_event(ctx, "converting", format="editor→api")
        client = ComfyUIClient(
            server_url=server_config.get("url", "http://127.0.0.1:8188"),
            auth=server_config.get("auth", ""),
        )
        try:
            object_info = client.get_object_info()
        except Exception as exc:
            output_error(ctx, "SERVER_ERROR",
                         f"Cannot fetch object_info for format conversion: {exc}",
                         hint="ComfyUI server must be online to convert editor-format workflows.")
            return
        api_data = _convert_editor_to_api(data, object_info)
        if not api_data:
            output_error(ctx, "CONVERSION_FAILED", "Failed to convert editor workflow to API format.")
            return
    else:
        output_error(ctx, "INVALID_FORMAT",
                     "Unrecognized workflow format. Expected ComfyUI API or editor format.")
        return

    # Generate schema
    parameters = _extract_schema(api_data, media_type)

    if preview:
        output_result(ctx, {
            "workflow_id": workflow_id,
            "server_id": server_id,
            "format_detected": format_detected,
            "parameters": parameters,
            "node_count": len(api_data),
            "preview": True,
        })
        return

    # Write files
    workflow_dir = _safe_path(base_dir, server_id, workflow_id)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    with open(workflow_dir / "workflow.json", "w", encoding="utf-8") as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    schema = {
        "description": "",
        "enabled": True,
        "parameters": parameters,
    }
    with open(workflow_dir / "schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    result: dict[str, Any] = {
        "workflow_id": workflow_id,
        "server_id": server_id,
        "format_detected": format_detected,
        "parameters_count": len(parameters),
        "node_count": len(api_data),
        "path": str(workflow_dir),
    }

    # Check for deprecated nodes
    try:
        repl_client = ComfyUIClient(
            server_url=server_config.get("url", "http://127.0.0.1:8188"),
            auth=server_config.get("auth", ""),
        )
        replacements = repl_client.get_node_replacements()
        if replacements:
            deprecated = []
            for node_id, node in api_data.items():
                if isinstance(node, dict):
                    ct = node.get("class_type", "")
                    if ct in replacements:
                        deprecated.append({"node_id": node_id, "old": ct, "new": replacements[ct]})
            if deprecated:
                result["deprecated_nodes"] = deprecated
    except Exception:
        pass

    # Optional deps check
    if check_deps:
        from .deps import _check_missing_models
        client = ComfyUIClient(
            server_url=server_config.get("url", "http://127.0.0.1:8188"),
            auth=server_config.get("auth", ""),
        )
        try:
            object_info = client.get_object_info()
            required_nodes = {
                node.get("class_type", "")
                for node in api_data.values()
                if isinstance(node, dict) and node.get("class_type")
            }
            installed_nodes = set(object_info.keys())
            missing_nodes = [
                {"class_type": ct, "can_auto_install": False}
                for ct in required_nodes if ct not in installed_nodes
            ]
            missing_models = _check_missing_models(client, api_data)
            result["deps"] = {
                "is_ready": len(missing_nodes) == 0 and len(missing_models) == 0,
                "missing_nodes": missing_nodes,
                "missing_models": missing_models,
            }
        except Exception:
            result["deps"] = {"error": "Could not check dependencies (server offline?)"}

    output_result(ctx, result)


def _import_from_server(
    ctx: typer.Context, base_dir: Path, server_id: str,
    server_config: dict[str, Any], name_filter: str,
    preview: bool, check_deps: bool, media_type: str = "image",
) -> None:
    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )

    try:
        workflow_paths = client.list_userdata_workflows()
    except Exception as exc:
        output_error(ctx, "SERVER_ERROR", f"Cannot list workflows from server: {exc}")
        return

    if not workflow_paths:
        output_error(ctx, "NO_WORKFLOWS", "No workflows found on the server.")
        return

    # Filter by name if provided
    if name_filter:
        workflow_paths = [p for p in workflow_paths if name_filter.lower() in p.lower()]
        if not workflow_paths:
            output_error(ctx, "NO_MATCH", f'No workflows matching "{name_filter}" found on server.')
            return

    if preview:
        output_result(ctx, {
            "server_id": server_id,
            "available_workflows": workflow_paths,
            "count": len(workflow_paths),
        })
        return

    # Import each workflow
    results = []
    for wf_path in workflow_paths:
        output_event(ctx, "importing", workflow=wf_path)
        data = client.read_userdata_workflow(wf_path)
        if data is None:
            results.append({"path": wf_path, "status": "failed", "error": "Could not read workflow"})
            continue

        # Detect and convert
        if _is_api_workflow(data):
            api_data = data
        elif _is_editor_workflow(data):
            try:
                object_info = client.get_object_info()
                api_data = _convert_editor_to_api(data, object_info)
            except Exception as exc:
                results.append({"path": wf_path, "status": "failed", "error": str(exc)})
                continue
        else:
            results.append({"path": wf_path, "status": "skipped", "error": "Unrecognized format"})
            continue

        filename = os.path.basename(wf_path)
        workflow_id = _suggest_workflow_id(api_data, filename)
        parameters = _extract_schema(api_data, media_type)

        workflow_dir = _safe_path(base_dir, server_id, workflow_id)
        workflow_dir.mkdir(parents=True, exist_ok=True)

        with open(workflow_dir / "workflow.json", "w", encoding="utf-8") as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)

        schema = {"description": "", "enabled": True, "parameters": parameters}
        with open(workflow_dir / "schema.json", "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

        entry: dict[str, Any] = {
            "path": wf_path,
            "workflow_id": workflow_id,
            "status": "imported",
            "parameters_count": len(parameters),
        }

        try:
            replacements = client.get_node_replacements()
            if replacements:
                deprecated = []
                for node_id, node in api_data.items():
                    if isinstance(node, dict):
                        ct = node.get("class_type", "")
                        if ct in replacements:
                            deprecated.append({"node_id": node_id, "old": ct, "new": replacements[ct]})
                if deprecated:
                    entry["deprecated_nodes"] = deprecated
        except Exception:
            pass

        results.append(entry)
        output_event(ctx, "imported", workflow_id=workflow_id)

    output_result(ctx, {
        "server_id": server_id,
        "results": results,
        "imported": sum(1 for r in results if r["status"] == "imported"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
    })


@app.command("enable")
def workflow_enable(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
):
    """Enable a workflow."""
    _toggle_workflow(ctx, skill_id, enabled=True)


@app.command("disable")
def workflow_disable(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
):
    """Disable a workflow."""
    _toggle_workflow(ctx, skill_id, enabled=False)


@app.command("delete")
def workflow_delete(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
):
    """Delete a workflow."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    server_id, workflow_id = _parse_skill_id(ctx, skill_id)

    try:
        workflow_dir = _safe_path(base_dir, server_id, workflow_id)
    except ValueError:
        output_error(ctx, "INVALID_PATH", f'Invalid skill ID: "{skill_id}"')
        return
    if not workflow_dir.is_dir():
        output_error(ctx, "SKILL_NOT_FOUND", f'Workflow "{skill_id}" not found.')
        return

    import shutil
    shutil.rmtree(workflow_dir)
    output_result(ctx, {
        "workflow_id": workflow_id,
        "server_id": server_id,
        "deleted": True,
    })


def _toggle_workflow(ctx: typer.Context, skill_id: str, enabled: bool) -> None:
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    server_id, workflow_id = _parse_skill_id(ctx, skill_id)

    try:
        workflow_dir = _safe_path(base_dir, server_id, workflow_id)
    except ValueError:
        output_error(ctx, "INVALID_PATH", f'Invalid skill ID: "{skill_id}"')
        return
    schema_path = workflow_dir / "schema.json"
    if not schema_path.exists():
        output_error(ctx, "SKILL_NOT_FOUND", f'Workflow "{skill_id}" not found.')
        return

    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    schema["enabled"] = enabled
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    output_result(ctx, {
        "workflow_id": workflow_id,
        "server_id": server_id,
        "enabled": enabled,
    })


def _parse_skill_id(ctx: typer.Context, skill_id: str) -> tuple[str, str]:
    if "/" in skill_id:
        server_id, workflow_id = skill_id.split("/", 1)
    else:
        base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
        config = load_config(base_dir)
        server_id = ctx.obj.get("server") or get_default_server_id(config)
        workflow_id = skill_id
    return server_id, workflow_id
