"""Shared helpers for curated resource commands."""

from __future__ import annotations

import json
from typing import Any, Optional

import typer

from ..runtime import RuntimeContext


def resolve_asset_id(
    asset_id: str | None,
    *,
    asset: str | None = None,
) -> str:
    """Accept ASSET_ID as a positional argument or --asset flag."""
    resolved = (asset_id or asset or "").strip()
    if not resolved:
        raise typer.BadParameter("Missing ASSET_ID. Pass it as an argument or --asset.")
    return resolved


def resolve_group_id(
    group_id: str | None,
    *,
    group: str | None = None,
) -> str:
    """Accept GROUP_ID as a positional argument or --group flag."""
    resolved = (group_id or group or "").strip()
    if not resolved:
        raise typer.BadParameter("Missing GROUP_ID. Pass it as an argument or --group.")
    return resolved


def parse_json_option(value: str | None, *, name: str) -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        if "=" in value:
            key, raw = value.split("=", 1)
            return {key.strip(): raw.strip()}
        raise typer.BadParameter(f"Invalid JSON for {name}")


def list_options(
    *,
    asset: bool = False,
    asset_required: bool = False,
    group: bool = False,
) -> dict[str, Any]:
    """Standard options for list commands."""
    opts: dict[str, Any] = {
        "detail": typer.Option("lite", "--detail", help="summary|lite|full|overview (resource-specific)."),
        "filter": typer.Option(None, "--filter", help="Filter JSON or key=value."),
        "sort": typer.Option(None, "--sort", help="Sort JSON."),
        "limit": typer.Option(100, "--limit", help="Max items to return."),
        "all_pages": typer.Option(False, "--all", help="Fetch all pages (ignores --limit)."),
        "page_size": typer.Option(100, "--page-size"),
        "max_pages": typer.Option(None, "--max-pages"),
        "after": typer.Option(None, "--after", help="Resume after this cursor."),
        "fields": typer.Option(None, "--fields", help="Comma-separated dot-path projection."),
        "dry_run": typer.Option(False, "--dry-run"),
    }
    if asset:
        opts["asset_id"] = typer.Option(
            None,
            "--asset",
            help="Asset ID." + (" Required." if asset_required else ""),
        )
    if group:
        opts["group_id"] = typer.Option(None, "--group", help="Asset group ID.")
    return opts


def run_list(
    ctx: typer.Context,
    *,
    method_name: str,
    asset_id: str | None = None,
    composed_asset_id: str | None = None,
    group_id: str | None = None,
    asset_group_ids: list[str] | None = None,
    filter_json: str | None = None,
    sort_json: str | None = None,
    limit: int = 100,
    all_pages: bool = False,
    page_size: int = 100,
    max_pages: int | None = None,
    after: str | None = None,
    fields: str | None = None,
    dry_run: bool = False,
    extra_kwargs: dict[str, Any] | None = None,
) -> None:
    runtime: RuntimeContext = ctx.obj
    if dry_run:
        runtime.emit_result(
            {
                "dry_run": True,
                "operation": method_name,
                "asset_id": asset_id,
                "composed_asset_id": composed_asset_id,
                "group_id": group_id,
                "after": after,
                "limit": None if all_pages else limit,
            }
        )
        return

    kwargs: dict[str, Any] = {"page_size": page_size, "max_pages": max_pages}
    if after is not None:
        kwargs["start_after"] = after
    if not all_pages:
        kwargs["max_items"] = limit
    if asset_id is not None:
        kwargs["asset_id"] = asset_id
    if composed_asset_id is not None:
        kwargs["composed_asset_id"] = composed_asset_id
    if group_id is not None:
        kwargs["group_id"] = group_id
    if asset_group_ids is not None:
        kwargs["asset_group_ids"] = asset_group_ids
    filt = parse_json_option(filter_json, name="--filter")
    if filt is not None:
        kwargs["filter"] = filt
    sort_val = parse_json_option(sort_json, name="--sort")
    if sort_val is not None:
        kwargs["sort"] = sort_val
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    sdk = runtime.get_client()
    method = getattr(sdk, method_name)
    field_list = [f.strip() for f in fields.split(",")] if fields else None
    item_limit = None if all_pages else limit
    runtime.emit_stream(
        method(**kwargs),
        fields=field_list,
        limit=item_limit,
    )


def run_graphql_by_name(
    ctx: typer.Context,
    *,
    method_name: str,
    input_model_name: str | None,
    input_param: str | None,
    payload: dict[str, Any],
    risk: str,
    dry_run: bool = False,
    yes: bool = False,
) -> None:
    runtime: RuntimeContext = ctx.obj
    if input_model_name and input_param:
        from netrise_turbine_sdk_graphql import input_types
        from pydantic import ValidationError

        from ..errors import format_validation_error
        from ..runtime import ExitCode

        model_cls = getattr(input_types, input_model_name)
        try:
            model = model_cls.model_validate(payload)
        except ValidationError as exc:
            runtime.emit_error(ExitCode.USAGE, format_validation_error(exc))
        kwargs = {input_param: model}
    else:
        kwargs = payload
    runtime.run_graphql_op(
        op_name=method_name,
        method_name=method_name,
        kwargs=kwargs,
        risk=risk,  # type: ignore[arg-type]
        dry_run=dry_run,
        yes=yes,
    )
