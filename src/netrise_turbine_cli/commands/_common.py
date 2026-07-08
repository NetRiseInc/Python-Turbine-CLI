"""Shared helpers for curated resource commands."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import typer

from ..runtime import RuntimeContext

# Shared help text so every list command documents the same syntax.
SORT_HELP = 'FIELD[:asc|desc], e.g. createdAt:desc. JSON also accepted: {"field":"CREATEDAT","order":"DESC"}.'
FILTER_HELP = 'Filter JSON (shape varies by resource; see docs) or key=value shorthand.'


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
        # Documented shorthand: key=value. Only apply it when the input
        # doesn't look like attempted JSON, so malformed JSON containing
        # '=' raises instead of being silently misparsed.
        if "=" in value and not value.lstrip().startswith(("{", "[", '"')):
            key, raw = value.split("=", 1)
            return {key.strip(): raw.strip()}
        raise typer.BadParameter(f"Invalid JSON for {name}")


_SORT_ORDERS = {
    "asc": "ASC",
    "ascending": "ASC",
    "desc": "DESC",
    "descending": "DESC",
}


def parse_sort_option(value: str | None, *, name: str = "--sort") -> Any:
    """Parse --sort as FIELD[:asc|desc] shorthand or raw sort JSON.

    Field names are normalized to the API's uppercase enum spelling, so
    `createdAt`, `created_at`, and `CREATEDAT` are all accepted. Server-side
    sort models share the {"field": ..., "order": ...} shape.
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if text.startswith(("{", "[")):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise typer.BadParameter(
                f'Invalid JSON for {name}. Shorthand also works: FIELD or FIELD:desc '
                f"(e.g. {name} createdAt:desc)."
            )
    field, sep, order = text.partition(":")
    normalized_field = re.sub(r"[^A-Za-z0-9]", "", field).upper()
    if not normalized_field:
        raise typer.BadParameter(
            f"{name} expects FIELD[:asc|desc] (e.g. createdAt:desc) or sort JSON."
        )
    result: dict[str, str] = {"field": normalized_field}
    if sep:
        normalized_order = _SORT_ORDERS.get(order.strip().lower())
        if normalized_order is None:
            raise typer.BadParameter(
                f"{name}: order must be asc or desc, got {order.strip()!r} "
                f"(e.g. {name} {field}:desc)."
            )
        result["order"] = normalized_order
    return result


def list_options(
    *,
    asset: bool = False,
    asset_required: bool = False,
    group: bool = False,
) -> dict[str, Any]:
    """Standard options for list commands."""
    opts: dict[str, Any] = {
        "detail": typer.Option("lite", "--detail", help="summary|lite|full|overview (resource-specific)."),
        "filter": typer.Option(None, "--filter", help=FILTER_HELP),
        "sort": typer.Option(None, "--sort", help=SORT_HELP),
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
    # Parse --filter/--sort before the dry-run exit so syntax errors surface
    # even in offline dry-run validation.
    filt = parse_json_option(filter_json, name="--filter")
    sort_val = parse_sort_option(sort_json, name="--sort")
    if dry_run:
        runtime.emit_result(
            {
                "dry_run": True,
                "operation": method_name,
                "asset_id": asset_id,
                "composed_asset_id": composed_asset_id,
                "group_id": group_id,
                "filter": filt,
                "sort": sort_val,
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
    if filt is not None:
        kwargs["filter"] = filt
    if sort_val is not None:
        kwargs["sort"] = sort_val
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    sdk = runtime.get_client()
    method = getattr(sdk, method_name)
    field_list = [f.strip() for f in fields.split(",")] if fields else None
    item_limit = None if all_pages else limit
    # The iterator is consumed lazily inside emit_stream, so SDK/network
    # errors surface there — keep the whole stream inside sdk_errors().
    with runtime.sdk_errors():
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
