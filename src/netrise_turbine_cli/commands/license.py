"""License issue resource commands."""

from __future__ import annotations

from typing import Optional

import typer

from ._common import resolve_asset_id, run_list

APP_NAME = "license"
APP_HELP = "License compliance issues."


def register(app: typer.Typer) -> None:
    app.command("list")(list_license_issues)


def list_license_issues(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    filter_json: Optional[str] = typer.Option(None, "--filter"),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List license issues for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    run_list(
        ctx,
        method_name="iter_license_issues",
        asset_id=aid,
        filter_json=filter_json,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )
