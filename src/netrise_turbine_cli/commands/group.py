"""Asset group resource commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ..runtime import RuntimeContext
from ._common import resolve_group_id, run_graphql_by_name, run_list

APP_NAME = "group"
APP_HELP = "Asset groups: list, members, and membership management."


def register(app: typer.Typer) -> None:
    app.command("list")(list_groups)
    app.command("members")(list_members)
    app.command("create")(create_group)
    app.command("update")(update_group)
    app.command("delete")(delete_group)
    app.command("add-assets")(add_assets)
    app.command("remove-assets")(remove_assets)


def list_groups(
    ctx: typer.Context,
    filter_json: Optional[str] = typer.Option(None, "--filter"),
    sort_json: Optional[str] = typer.Option(None, "--sort"),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List asset groups."""
    run_list(
        ctx,
        method_name="iter_asset_groups",
        filter_json=filter_json,
        sort_json=sort_json,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def list_members(
    ctx: typer.Context,
    group_id: Optional[str] = typer.Argument(None, help="Group ID (or use --group)."),
    group: Optional[str] = typer.Option(None, "--group", help="Group ID."),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List members of an asset group."""
    gid = resolve_group_id(group_id, group=group)
    run_list(
        ctx,
        method_name="iter_asset_group_members",
        group_id=gid,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def create_group(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name"),
    description: Optional[str] = typer.Option(None, "--description"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Create an asset group."""
    payload: dict[str, str] = {"name": name}
    if description:
        payload["description"] = description
    run_graphql_by_name(
        ctx,
        method_name="mutation_create_asset_group",
        input_model_name="CreateAssetGroupInput",
        input_param="create_asset_group_args",
        payload=payload,
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def update_group(
    ctx: typer.Context,
    group_id: str = typer.Option(..., "--id"),
    name: Optional[str] = typer.Option(None, "--name"),
    description: Optional[str] = typer.Option(None, "--description"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Update an asset group."""
    payload: dict[str, str] = {"id": group_id}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    run_graphql_by_name(
        ctx,
        method_name="mutation_update_asset_group",
        input_model_name="UpdateAssetGroupInput",
        input_param="update_asset_group_args",
        payload=payload,
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def delete_group(
    ctx: typer.Context,
    group_id: Optional[str] = typer.Argument(None, help="Group ID (or use --group)."),
    group: Optional[str] = typer.Option(None, "--group", help="Group ID."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Delete an asset group."""
    gid = resolve_group_id(group_id, group=group)
    run_graphql_by_name(
        ctx,
        method_name="mutation_delete_asset_group",
        input_model_name="DeleteAssetGroupInput",
        input_param="delete_asset_group_args",
        payload={"id": gid},
        risk="destructive",
        dry_run=dry_run,
        yes=yes,
    )


def add_assets(
    ctx: typer.Context,
    group_id: str = typer.Option(..., "--id"),
    input_json: Optional[str] = typer.Option(None, "--input", "-i"),
    input_file: Optional[Path] = typer.Option(None, "--input-file"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Add assets to a group."""
    runtime: RuntimeContext = ctx.obj
    payload = runtime.load_input_payload(input_json, input_file)
    payload["id"] = group_id
    run_graphql_by_name(
        ctx,
        method_name="mutation_add_assets_to_asset_group",
        input_model_name="AddAssetsToAssetGroupInput",
        input_param="add_assets_to_asset_group_args",
        payload=payload,
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def remove_assets(
    ctx: typer.Context,
    group_id: str = typer.Option(..., "--id"),
    input_json: Optional[str] = typer.Option(None, "--input", "-i"),
    input_file: Optional[Path] = typer.Option(None, "--input-file"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Remove assets from a group."""
    runtime: RuntimeContext = ctx.obj
    payload = runtime.load_input_payload(input_json, input_file)
    payload["id"] = group_id
    run_graphql_by_name(
        ctx,
        method_name="mutation_remove_assets_from_asset_group",
        input_model_name="RemoveAssetsFromAssetGroupInput",
        input_param="remove_assets_from_asset_group_args",
        payload=payload,
        risk="destructive",
        dry_run=dry_run,
        yes=yes,
    )
