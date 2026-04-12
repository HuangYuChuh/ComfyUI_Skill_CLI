"""comfyui-skill upload — upload files to ComfyUI server."""

from __future__ import annotations

import os
import tempfile
from typing import Optional

import typer

from ..client import ComfyUIClient
from ..config import get_base_dir, get_default_server_id, get_server, load_config
from ..output import output_error, output_result


def upload_cmd(
    ctx: typer.Context,
    file_path: Optional[str] = typer.Argument(None, help="Path to file (image, mask, audio, etc.)"),
    from_output: str = typer.Option("", "--from-output", help="Prompt ID — reuse an output from a previous run as input"),
    mask: bool = typer.Option(False, "--mask", help="Upload as mask (for inpainting workflows)"),
    original: str = typer.Option("", "--original", help="Original image filename (for mask upload)"),
):
    """Upload a file to ComfyUI for use in workflows.

    Either provide a local file path, or use --from-output to chain a previous
    workflow's output as input for the next one.
    """
    if not file_path and not from_output:
        output_error(ctx, "MISSING_INPUT", "Provide a file path or --from-output <prompt_id>.")
        return

    if file_path and from_output:
        output_error(ctx, "CONFLICTING_INPUT", "Provide either a file path or --from-output, not both.")
        return

    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or get_default_server_id(config)
    server_config = get_server(config, server_id)

    if not server_config:
        output_error(ctx, "SERVER_NOT_FOUND", f'Server "{server_id}" not found.')
        return

    client = ComfyUIClient(
        server_url=server_config.get("url", "http://127.0.0.1:8188"),
        auth=server_config.get("auth", ""),
    )

    if from_output:
        _upload_from_output(ctx, client, server_id, from_output)
    else:
        _upload_local_file(ctx, client, server_id, file_path, mask, original)


def _upload_local_file(
    ctx: typer.Context,
    client: ComfyUIClient,
    server_id: str,
    file_path: str,
    mask: bool = False,
    original: str = "",
) -> None:
    if not os.path.isfile(file_path):
        output_error(ctx, "FILE_NOT_FOUND", f'File not found: "{file_path}"')
        return

    try:
        if mask:
            result = client.upload_mask(file_path, original)
        else:
            result = client.upload_file(file_path)
        output_result(ctx, {
            "name": result.get("name", ""),
            "subfolder": result.get("subfolder", ""),
            "type": result.get("type", "input"),
            "server_id": server_id,
        })
    except Exception as exc:
        output_error(ctx, "UPLOAD_FAILED", f"Upload failed: {exc}")


def _upload_from_output(
    ctx: typer.Context,
    client: ComfyUIClient,
    server_id: str,
    prompt_id: str,
) -> None:
    # Find the output from history
    history = client.get_history(prompt_id)
    if not history:
        output_error(ctx, "NOT_FOUND", f"No history found for prompt_id: {prompt_id}")
        return

    outputs = history.get("outputs", {})
    if not outputs:
        output_error(ctx, "NO_OUTPUTS", f"Prompt {prompt_id} has no outputs.")
        return

    # Collect first output file
    target = None
    for node_output in outputs.values():
        if not isinstance(node_output, dict):
            continue
        for key in ("images", "gifs", "audio", "video"):
            items = node_output.get(key, [])
            if items:
                target = items[0]
                break
        if target:
            break

    if not target:
        output_error(ctx, "NO_OUTPUTS", f"No output files found for prompt {prompt_id}.")
        return

    filename = target.get("filename", "")
    subfolder = target.get("subfolder", "")
    output_type = target.get("type", "output")

    try:
        # Download from ComfyUI /view endpoint
        data = client.download_output(filename, subfolder, output_type)

        # Write to temp file and re-upload to input
        suffix = os.path.splitext(filename)[1] or ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, prefix="chain_", delete=False) as f:
            f.write(data)
            tmp_path = f.name

        try:
            result = client.upload_file(tmp_path)
            output_result(ctx, {
                "name": result.get("name", ""),
                "subfolder": result.get("subfolder", ""),
                "type": result.get("type", "input"),
                "server_id": server_id,
                "source_prompt_id": prompt_id,
                "source_filename": filename,
            })
        finally:
            os.unlink(tmp_path)

    except Exception as exc:
        output_error(ctx, "CHAIN_FAILED", f"Failed to chain output: {exc}")
