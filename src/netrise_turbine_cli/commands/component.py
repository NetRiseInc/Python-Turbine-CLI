"""Component / dependency resource commands."""

from __future__ import annotations

from typing import Optional

import typer

from ._common import resolve_asset_id, run_list
from ._registry import COMPONENT_LIST_METHODS

APP_NAME = "component"
APP_HELP = "Software components and dependencies (SBOM)."


def register(app: typer.Typer) -> None:
    app.command("list")(list_components)
    app.command("grouped")(grouped_components)
    app.command("crypto")(crypto_libraries)


def list_components(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    detail: str = typer.Option("lite", "--detail", help="lite|full"),
    filter_json: Optional[str] = typer.Option(None, "--filter"),
    sort_json: Optional[str] = typer.Option(None, "--sort"),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List dependencies for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    method = COMPONENT_LIST_METHODS.get(detail, COMPONENT_LIST_METHODS["lite"])
    run_list(
        ctx,
        method_name=method,
        composed_asset_id=aid,
        filter_json=filter_json,
        sort_json=sort_json,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def grouped_components(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    grouped_by: Optional[str] = typer.Option(None, "--group-by"),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List grouped dependency rollups."""
    aid = resolve_asset_id(asset_id, asset=asset)
    extra: dict[str, str] = {}
    if grouped_by:
        extra["grouped_by"] = grouped_by
    run_list(
        ctx,
        method_name="iter_grouped_dependencies",
        composed_asset_id=aid,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
        extra_kwargs=extra or None,
    )


def crypto_libraries(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List crypto libraries in an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    run_list(
        ctx,
        method_name="iter_list_asset_crypto_libraries",
        asset_id=aid,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )
