"""comfyui-skill models — discover available models on ComfyUI server."""

from __future__ import annotations

from typing import Optional

import typer

from ..output import output_error, output_result
from ..utils import build_client

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def models_list(
    ctx: typer.Context,
    folder: Optional[str] = typer.Argument(None, help="Model folder (e.g., checkpoints, loras, vae). Omit to list all folders."),
):
    """List available models. Specify a folder to see its contents, or omit to list all folders."""
    client, server_id = build_client(ctx)

    try:
        if folder:
            models = client.get_models(folder)
            output_result(ctx, {
                "server_id": server_id,
                "folder": folder,
                "models": models,
                "count": len(models),
            })
        else:
            folders = client.get_model_folders()
            output_result(ctx, {
                "server_id": server_id,
                "folders": folders,
            })
    except Exception as exc:
        output_error(ctx, "MODELS_FAILED", f"Failed to list models: {exc}")
        return


@app.command("embeddings")
def models_embeddings(ctx: typer.Context):
    """List available text embeddings."""
    client, server_id = build_client(ctx)
    try:
        embeddings = client.get_embeddings()
        output_result(ctx, {"server_id": server_id, "embeddings": embeddings, "count": len(embeddings)})
    except Exception as exc:
        output_error(ctx, "EMBEDDINGS_FAILED", f"Failed to list embeddings: {exc}")
        return


@app.command("metadata")
def models_metadata(
    ctx: typer.Context,
    folder: str = typer.Argument(help="Model folder (e.g., checkpoints, loras)"),
    filename: str = typer.Argument(help="Model filename"),
):
    """Show safetensors metadata for a model file."""
    client, server_id = build_client(ctx)
    try:
        data = client.get_model_metadata(folder, filename)
    except Exception as exc:
        output_error(ctx, "METADATA_FAILED", f"Failed to fetch metadata: {exc}")
        return

    if not data:
        output_error(ctx, "NO_METADATA", f"No metadata found for {folder}/{filename}")
        return
    output_result(ctx, {"server_id": server_id, "folder": folder, "filename": filename, "metadata": data})
