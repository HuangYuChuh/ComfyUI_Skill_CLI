"""ComfyUI Skill CLI — Typer app with global options and subcommand registration."""

from __future__ import annotations

import typer

from .commands import deps, run, server, skill, upload, workflow

app = typer.Typer(
    name="comfyui-skill",
    help="ComfyUI Skill CLI — Agent-friendly workflow management",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback()
def main(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output (shortcut for --output-format json)"),
    output_format: str = typer.Option("", "--output-format", help="Output format: text, json, stream-json"),
    server_id: str = typer.Option("", "--server", "-s", help="Server ID"),
    base_dir: str = typer.Option("", "--dir", "-d", help="Data directory (default: current directory)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["output_format"] = output_format
    ctx.obj["server"] = server_id
    ctx.obj["base_dir"] = base_dir
    ctx.obj["verbose"] = verbose


# Subcommand groups — each needs a callback to inherit parent context
for sub_app in [deps.app, server.app, workflow.app]:
    @sub_app.callback()
    def _pass_context(ctx: typer.Context):
        if ctx.parent and ctx.parent.obj:
            ctx.ensure_object(dict)
            ctx.obj.update(ctx.parent.obj)

app.add_typer(deps.app, name="deps", help="Manage dependencies")
app.add_typer(server.app, name="server", help="Manage servers")
app.add_typer(workflow.app, name="workflow", help="Manage workflows")

# Top-level commands
app.command("list")(skill.skill_list)
app.command("info")(skill.skill_info)
app.command("run")(run.run_cmd)
app.command("submit")(run.submit_cmd)
app.command("status")(run.status_cmd)
app.command("upload")(upload.upload_cmd)
