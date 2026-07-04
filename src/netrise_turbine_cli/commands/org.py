"""Organization resource commands."""

from __future__ import annotations

import typer

APP_NAME = "org"
APP_HELP = "Organization settings and metadata."


def register(app: typer.Typer) -> None:
    app.command("info")(org_info)
    app.command("settings")(org_settings)


def org_info(ctx: typer.Context) -> None:
    """Show organization-level information."""
    from ._common import run_graphql_by_name

    run_graphql_by_name(
        ctx,
        method_name="query_org_level_information",
        input_model_name=None,
        input_param=None,
        payload={},
        risk="read",
    )


def org_settings(ctx: typer.Context) -> None:
    """Show organization-level settings."""
    from ._common import run_graphql_by_name

    run_graphql_by_name(
        ctx,
        method_name="query_org_level_settings",
        input_model_name=None,
        input_param=None,
        payload={},
        risk="read",
    )
