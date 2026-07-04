"""Auth commands."""

from __future__ import annotations

from typing import Optional

import typer

from ..config import load_cli_config, save_cli_config
from ..runtime import ExitCode, RuntimeContext

APP_NAME = "auth"
APP_HELP = "Authentication and configuration."


def register(app: typer.Typer) -> None:
    app.command("status")(status)
    app.command("login")(login)


def status(ctx: typer.Context) -> None:
    """Show current auth configuration (redacted)."""
    runtime: RuntimeContext = ctx.obj
    try:
        cfg = load_cli_config()
    except ValueError as exc:
        runtime.emit_error(ExitCode.USAGE, str(exc))
    data = {
        "endpoint": cfg.endpoint,
        "organization_id": cfg.organization_id,
        "domain": cfg.domain,
        "audience": cfg.audience,
        "authenticated": bool(
            cfg.turbine_api_token or (cfg.client_id and cfg.client_secret)
        ),
    }
    runtime.emit_result(data)


def login(
    ctx: typer.Context,
    endpoint: Optional[str] = typer.Option(None, "--endpoint", help="GraphQL endpoint URL."),
    org: Optional[str] = typer.Option(None, "--org", help="Organization ID."),
    save: bool = typer.Option(False, "--save", help="Save non-secret settings to ~/.config/turbine/config.toml."),
) -> None:
    """Verify credentials and optionally persist config."""
    runtime: RuntimeContext = ctx.obj
    if endpoint:
        runtime.endpoint = endpoint
    if org:
        runtime.org = org
    client = runtime.get_client()
    cfg = client.config
    runtime.emit_result(
        {
            "status": "ok",
            "endpoint": cfg.endpoint,
            "organization_id": cfg.organization_id,
        }
    )
    if save:
        path = save_cli_config(
            {
                "endpoint": cfg.endpoint,
                "organization_id": cfg.organization_id,
                "domain": cfg.domain,
                "audience": cfg.audience,
                "client_id": cfg.client_id,
            }
        )
        typer.echo(f"Saved config to {path}", err=True)
