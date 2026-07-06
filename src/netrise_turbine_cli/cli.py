"""Turbine CLI entry point."""

from __future__ import annotations

import os
from typing import Optional

import rich_click as click
import typer
from typer.core import TyperGroup

from .commands import register_curated_commands
from .commands_api import api_app
from .runtime import ExitCode, RuntimeContext

click.rich_click.STYLE_HELPS = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True


class RichTyperGroup(TyperGroup, click.RichGroup):
    pass


def _version_callback(value: bool) -> None:
    if value:
        from . import __version__

        typer.echo(__version__)
        raise typer.Exit()


app = typer.Typer(
    cls=RichTyperGroup,
    name="turbine",
    help="NetRise Turbine CLI — resource commands for humans and agents.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)


def _attach_output_option(ctx: typer.Context, output: str) -> None:
    if output not in {"auto", "json", "table"}:
        typer.echo("Invalid --output (use auto, json, or table)", err=True)
        raise typer.Exit(code=int(ExitCode.USAGE))
    if ctx.obj is None:
        ctx.obj = RuntimeContext(output=output)  # type: ignore[assignment]
    else:
        ctx.obj.output = output  # type: ignore[union-attr]


@app.callback()
def _root_callback(
    ctx: typer.Context,
    output: str = typer.Option("auto", "--output", "-o", help="auto|json|table"),
    endpoint: Optional[str] = typer.Option(None, "--endpoint", help="Override GraphQL endpoint."),
    org: Optional[str] = typer.Option(None, "--org", help="Override organization_id."),
    version: Optional[bool] = typer.Option(None, "--version", callback=_version_callback, is_eager=True),
) -> None:
    _attach_output_option(ctx, output)
    runtime: RuntimeContext = ctx.obj
    runtime.endpoint = endpoint
    runtime.org = org


register_curated_commands(app, group_cls=RichTyperGroup)
app.add_typer(api_app, name="api")


def _register_generated() -> None:
    from ._generated.commands import register_api_commands

    register_api_commands(api_app)


_register_generated()


def main() -> None:
    import sys

    _preparse_global_output(sys.argv)
    app()


def _preparse_global_output(argv: list[str]) -> None:
    """Allow --output/-o anywhere in the argv list."""
    output: str | None = None
    cleaned = [argv[0]]
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in ("-o", "--output") and i + 1 < len(argv):
            output = argv[i + 1]
            i += 2
            continue
        cleaned.append(arg)
        i += 1
    if output is not None:
        os.environ["TURBINE_OUTPUT"] = output
    argv[:] = cleaned


if __name__ == "__main__":
    main()
