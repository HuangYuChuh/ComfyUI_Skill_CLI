"""comfy-skills skill list / info"""

from __future__ import annotations

import typer

from ..config import get_base_dir, get_default_server_id, get_servers, load_config
from ..output import output_error, output_result
from ..storage import get_workflow_detail, list_workflows

app = typer.Typer()


@app.command("list")
def skill_list(ctx: typer.Context):
    """List all available skills."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))
    config = load_config(base_dir)
    server_id = ctx.obj.get("server") or ""

    all_skills = []
    if server_id:
        all_skills = list_workflows(base_dir, server_id)
    else:
        for s in get_servers(config):
            if s.get("enabled", True):
                all_skills.extend(list_workflows(base_dir, s["id"]))

    output_result(ctx, all_skills)


@app.command("info")
def skill_info(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID in format: server_id/workflow_id"),
):
    """Show skill details including parameter schema."""
    base_dir = get_base_dir(ctx.obj.get("base_dir", ""))

    if "/" in skill_id:
        server_id, workflow_id = skill_id.split("/", 1)
    else:
        config = load_config(base_dir)
        server_id = ctx.obj.get("server") or get_default_server_id(config)
        workflow_id = skill_id

    detail = get_workflow_detail(base_dir, server_id, workflow_id)
    if detail is None:
        output_error(ctx, "SKILL_NOT_FOUND", f'Skill "{skill_id}" not found.',
                     hint="Run `comfy-skills skill list` to see available skills.")

    # Don't include full workflow_data in info output (too large)
    detail.pop("workflow_data", None)
    output_result(ctx, detail)
