"""Misconfiguration resource commands."""

from __future__ import annotations

from typing import Optional

import typer

from ._common import FILTER_HELP, resolve_asset_id, run_list
from ._registry import MISCONFIG_LIST_METHODS

APP_NAME = "misconfig"
APP_HELP = "Misconfiguration findings."


def register(app: typer.Typer) -> None:
    app.command("list")(list_misconfigs)


def list_misconfigs(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    detail: str = typer.Option("lite", "--detail", help="lite|full"),
    filter_json: Optional[str] = typer.Option(None, "--filter", help=FILTER_HELP),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List misconfigurations for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    method = MISCONFIG_LIST_METHODS.get(detail, MISCONFIG_LIST_METHODS["lite"])
    run_list(
        ctx,
        method_name=method,
        asset_id=aid,
        filter_json=filter_json,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )
