"""ComfyUI Skill CLI — Typer app with global options and subcommand registration."""

from __future__ import annotations

import typer

from . import __version__
from .commands import cancel, config, deps, free, history, queue, run, server, skill, upload, workflow
from .update_check import is_machine_output, maybe_notify_update

app = typer.Typer(
    name="comfyui-skill",
    help="ComfyUI Skill CLI — Agent-friendly workflow management",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"comfyui-skill {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", callback=_version_callback, is_eager=True, help="Show version and exit"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output (shortcut for --output-format json)"),
    output_format: str = typer.Option("", "--output-format", help="Output format: text, json, stream-json"),
    server_id: str = typer.Option("", "--server", "-s", help="Server ID"),
    base_dir: str = typer.Option("", "--dir", "-d", help="Data directory (default: current directory)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    no_update_check: bool = typer.Option(False, "--no-update-check", help="Skip automatic CLI update check"),
):
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["output_format"] = output_format
    ctx.obj["server"] = server_id
    ctx.obj["base_dir"] = base_dir
    ctx.obj["verbose"] = verbose
    ctx.obj["no_update_check"] = no_update_check

    maybe_notify_update(
        __version__,
        disabled=no_update_check or is_machine_output(json_output, output_format),
    )


# Subcommand groups — each needs a callback to inherit parent context
for sub_app in [config.app, deps.app, history.app, queue.app, server.app, workflow.app]:
    @sub_app.callback()
    def _pass_context(ctx: typer.Context):
        if ctx.parent and ctx.parent.obj:
            ctx.ensure_object(dict)
            ctx.obj.update(ctx.parent.obj)

app.add_typer(config.app, name="config", help="Import/export configuration")
app.add_typer(deps.app, name="deps", help="Manage dependencies")
app.add_typer(history.app, name="history", help="Execution history")
app.add_typer(queue.app, name="queue", help="View and manage execution queue")
app.add_typer(server.app, name="server", help="Manage servers")
app.add_typer(workflow.app, name="workflow", help="Manage workflows")

# Top-level commands
app.command("list")(skill.skill_list)
app.command("info")(skill.skill_info)
app.command("run")(run.run_cmd)
app.command("submit")(run.submit_cmd)
app.command("status")(run.status_cmd)
app.command("upload")(upload.upload_cmd)
app.command("cancel")(cancel.cancel_cmd)
app.command("free")(free.free_cmd)
