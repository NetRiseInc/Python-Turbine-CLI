"""Curated resource commands package."""

from __future__ import annotations

import typer

from . import (
    asset,
    auth,
    cert,
    component,
    credential,
    group,
    key,
    license,
    misconfig,
    notification,
    org,
    protection,
    report,
    search,
    secret,
    skill,
    user,
    vuln,
)

RichTyperGroup = typer.Typer  # replaced at registration time


def register_curated_commands(app: typer.Typer, *, group_cls: type) -> None:
    """Attach all resource command groups to the root CLI."""
    for module in (
        auth,
        asset,
        vuln,
        group,
        component,
        secret,
        credential,
        cert,
        key,
        misconfig,
        license,
        protection,
        user,
        org,
        notification,
        report,
        skill,
    ):
        sub = typer.Typer(name=module.APP_NAME, help=module.APP_HELP, cls=group_cls)
        module.register(sub)
        app.add_typer(sub)

    # `search` is a single verb, not a resource group: register it at the root
    # so the documented `turbine search <term>` invocation works.
    app.command(search.APP_NAME, help=search.APP_HELP)(search.search)
