"""Cryptographic key resource commands."""

from __future__ import annotations

from typing import Optional

import typer

from ._common import FILTER_HELP, resolve_asset_id, run_list
from ._registry import KEY_LIST_METHODS

APP_NAME = "key"
APP_HELP = "Private and public keys found in firmware."


def register(app: typer.Typer) -> None:
    app.command("list")(list_keys)


def list_keys(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    key_type: str = typer.Option("private", "--type", help="private|public"),
    filter_json: Optional[str] = typer.Option(None, "--filter", help=FILTER_HELP),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List cryptographic keys for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    method = KEY_LIST_METHODS.get(key_type, KEY_LIST_METHODS["private"])
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
