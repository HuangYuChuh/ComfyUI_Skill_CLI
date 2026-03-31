"""comfy-skills deps check / install — placeholder for dependency management."""

from __future__ import annotations

import typer

from ..output import output_result

app = typer.Typer()


@app.command("check")
def deps_check(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
):
    """Check if a skill's dependencies are installed."""
    # TODO: Implement dependency checking (query /object_info, compare with workflow nodes)
    output_result(ctx, {
        "skill_id": skill_id,
        "status": "not_implemented",
        "message": "Dependency checking will be implemented in a future version.",
    })


@app.command("install")
def deps_install(
    ctx: typer.Context,
    skill_id: str = typer.Argument(help="Skill ID: server_id/workflow_id"),
):
    """Install missing dependencies for a skill."""
    # TODO: Implement dependency installation (Manager API / comfy-cli bridge)
    output_result(ctx, {
        "skill_id": skill_id,
        "status": "not_implemented",
        "message": "Dependency installation will be implemented in a future version.",
    })
