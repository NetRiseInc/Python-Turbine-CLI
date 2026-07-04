"""Asset resource commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ..runtime import RuntimeContext
from ._common import resolve_asset_id, run_graphql_by_name, run_list
from ._registry import ASSET_LIST_METHODS

APP_NAME = "asset"
APP_HELP = "Assets: list, inspect, upload, and manage firmware/SBOMs."


def register(app: typer.Typer) -> None:
    app.command("list")(list_assets)
    app.command("get")(get_asset)
    app.command("status")(asset_status)
    app.command("files")(asset_files)
    app.command("upload")(upload_asset)
    app.command("upload-dir")(upload_assets)
    app.command("submit")(submit_asset)
    app.command("update")(update_asset)
    app.command("activity")(asset_activity)
    app.command("hashes")(asset_hashes)


def list_assets(
    ctx: typer.Context,
    detail: str = typer.Option("lite", "--detail", help="summary|lite|full|overview"),
    filter_json: Optional[str] = typer.Option(None, "--filter"),
    sort_json: Optional[str] = typer.Option(None, "--sort"),
    limit: int = typer.Option(100, "--limit"),
    all_pages: bool = typer.Option(False, "--all"),
    page_size: int = typer.Option(100, "--page-size"),
    max_pages: Optional[int] = typer.Option(None, "--max-pages"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List assets with pagination."""
    method = ASSET_LIST_METHODS.get(detail, ASSET_LIST_METHODS["lite"])
    run_list(
        ctx,
        method_name=method,
        filter_json=filter_json,
        sort_json=sort_json,
        limit=limit,
        all_pages=all_pages,
        page_size=page_size,
        max_pages=max_pages,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def get_asset(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Get a single asset by ID."""
    aid = resolve_asset_id(asset_id, asset=asset)
    run_graphql_by_name(
        ctx,
        method_name="query_asset",
        input_model_name="AssetInput",
        input_param="asset_args",
        payload={"assetId": aid},
        risk="read",
        dry_run=dry_run,
    )


def asset_status(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Check asset processing status."""
    aid = resolve_asset_id(asset_id, asset=asset)
    run_graphql_by_name(
        ctx,
        method_name="query_asset_status",
        input_model_name="AssetStatusInput",
        input_param="asset_status_args",
        payload={"assetId": aid},
        risk="read",
        dry_run=dry_run,
    )


def asset_files(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
) -> None:
    """List all files for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    runtime: RuntimeContext = ctx.obj
    runtime.run_curated_op(
        op_name="list_files",
        method_name="list_files",
        call=lambda sdk: sdk.list_files(aid),
        risk="read",
        dry_run=False,
        yes=False,
    )


def upload_asset(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Firmware or SBOM file."),
    name: Optional[str] = typer.Option(None, "--name"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Upload a single file as an asset."""
    runtime: RuntimeContext = ctx.obj
    runtime.run_curated_op(
        op_name="upload_asset",
        method_name="upload_asset",
        call=lambda sdk: sdk.upload_asset(path, name=name),
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def upload_assets(
    ctx: typer.Context,
    directory: Path = typer.Argument(..., help="Directory of firmware files."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Upload all files in a directory as assets."""
    runtime: RuntimeContext = ctx.obj
    runtime.run_curated_op(
        op_name="upload_assets",
        method_name="upload_assets",
        call=lambda sdk: sdk.upload_assets(directory),
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def submit_asset(
    ctx: typer.Context,
    input_json: Optional[str] = typer.Option(None, "--input", "-i"),
    input_file: Optional[Path] = typer.Option(None, "--input-file"),
    name: Optional[str] = typer.Option(None, "--name"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Submit asset metadata and upload."""
    runtime: RuntimeContext = ctx.obj
    payload = runtime.load_input_payload(input_json, input_file)
    if name:
        payload["name"] = name
    run_graphql_by_name(
        ctx,
        method_name="mutation_asset_submit",
        input_model_name="SubmitAssetInput",
        input_param="asset_submit_args",
        payload=payload,
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def update_asset(
    ctx: typer.Context,
    asset_id: str = typer.Option(..., "--id", help="Asset ID."),
    input_json: Optional[str] = typer.Option(None, "--input", "-i"),
    input_file: Optional[Path] = typer.Option(None, "--input-file"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Update asset metadata."""
    runtime: RuntimeContext = ctx.obj
    payload = runtime.load_input_payload(input_json, input_file)
    payload["id"] = asset_id
    run_graphql_by_name(
        ctx,
        method_name="mutation_asset_update",
        input_model_name="UpdateAssetInput",
        input_param="asset_update_args",
        payload=payload,
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def asset_activity(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List activity log entries for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    run_list(
        ctx,
        method_name="iter_activity",
        asset_id=aid,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def asset_hashes(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List file hashes for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    run_list(
        ctx,
        method_name="iter_hashes",
        asset_id=aid,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )
