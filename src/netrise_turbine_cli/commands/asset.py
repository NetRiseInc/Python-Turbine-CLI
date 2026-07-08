"""Asset resource commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import typer

from ..runtime import RuntimeContext
from ._common import FILTER_HELP, SORT_HELP, resolve_asset_id, run_graphql_by_name, run_list
from ._registry import ASSET_LIST_METHODS

APP_NAME = "asset"
APP_HELP = "Assets: list, inspect, upload, and manage firmware/SBOMs."


def register(app: typer.Typer) -> None:
    app.command("list")(list_assets)
    app.command("get")(get_asset)
    app.command("risk")(asset_risk)
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
    filter_json: Optional[str] = typer.Option(None, "--filter", help=FILTER_HELP),
    sort_json: Optional[str] = typer.Option(None, "--sort", help=SORT_HELP),
    limit: int = typer.Option(100, "--limit"),
    all_pages: bool = typer.Option(False, "--all"),
    page_size: int = typer.Option(100, "--page-size"),
    max_pages: Optional[int] = typer.Option(None, "--max-pages"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
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


def _analytic_summary(aid: str, asset: Any) -> dict[str, Any]:
    """Reshape query_asset's analytic block into a one-look risk summary."""
    analytic = getattr(asset, "analytic", None)
    risk = getattr(asset, "risk", None)

    def block(obj: Any) -> dict[str, Any]:
        return obj.model_dump(mode="json", by_alias=True) if obj is not None else {}

    vuln = block(getattr(analytic, "vulnerability", None))
    vuln_total = sum(v for v in vuln.values() if isinstance(v, int))
    creds = block(getattr(analytic, "credentials", None))
    misconfig = block(getattr(analytic, "misconfigurations", None))
    crypto = block(getattr(analytic, "cryptography", None))
    exploit = block(getattr(analytic, "exploit", None))

    return {
        "assetId": aid,
        "name": getattr(asset, "name", None),
        "risk": {
            "category": getattr(risk, "category", None),
            "score": getattr(risk, "score", None),
        },
        "findings": {
            "vulnerabilities": {
                **vuln,
                "total": vuln_total,
                "drillDown": f"turbine vuln list {aid} --detail lite",
            },
            "exploitExposure": {
                **exploit,
                "drillDown": f"turbine vuln list {aid} --detail detailed-lite",
            },
            "misconfigurations": {
                **misconfig,
                "drillDown": f"turbine misconfig list {aid}",
            },
            "secretsAndCredentials": {
                **creds,
                "drillDown": f"turbine secret list {aid} / turbine credential list {aid}",
            },
            "cryptography": {
                **crypto,
                "drillDown": f"turbine cert list {aid} / turbine key list {aid}",
            },
            "licenseIssues": {
                "count": getattr(analytic, "license_issues", None),
                "drillDown": f"turbine license list {aid}",
            },
        },
    }


def asset_risk(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset / --latest)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    latest: bool = typer.Option(
        False, "--latest", help="Use the most recently created asset in the org."
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """One-call risk summary: score plus finding counts across every category.

    Answers broad questions like "what risk does this asset carry?" in a
    single call; each category includes the drill-down command for details.
    """
    runtime: RuntimeContext = ctx.obj
    if latest and (asset_id or asset):
        raise typer.BadParameter("Pass an asset ID or --latest, not both.")
    if not latest:
        # Validate early so the error names all the ways to supply an ID.
        aid = (asset_id or asset or "").strip()
        if not aid:
            raise typer.BadParameter(
                "Missing ASSET_ID. Pass it as an argument, --asset, or use --latest."
            )
    if dry_run:
        runtime.emit_result(
            {
                "dry_run": True,
                "operation": "asset_risk",
                "asset_id": None if latest else aid,
                "latest": latest,
            }
        )
        return

    from netrise_turbine_sdk_graphql.input_types import AssetInput

    from ..runtime import ExitCode, _strip_composed_suffix

    with runtime.sdk_errors():
        sdk = runtime.get_client()
        if latest:
            newest = list(
                sdk.iter_assets_relay_lite(
                    sort={"field": "CREATEDAT", "order": "DESC"},
                    page_size=1,
                    max_items=1,
                )
            )
            if not newest:
                runtime.emit_error(ExitCode.GRAPHQL, "No assets found in the organization.")
            aid = _strip_composed_suffix(newest[0].id)
        result = sdk.graphql().query_asset(asset_args=AssetInput(assetId=aid)).asset
        if result is None:
            runtime.emit_error(ExitCode.GRAPHQL, f"Asset not found: {aid}")
        runtime.emit_result(_analytic_summary(aid, result))


def _poll_heartbeat(runtime: RuntimeContext) -> Callable[[dict[str, Any]], None]:
    """Progress lines on stderr while --wait polls (stdout stays data-only)."""

    def _cb(info: dict[str, Any]) -> None:
        if info.get("has_running_job") is False:
            return
        if runtime.is_agent_mode:
            payload = {
                "waiting": info["phase"],
                "asset_id": info.get("asset_id"),
                "upload_id": info.get("upload_id"),
                "elapsed_s": int(info["elapsed"]),
            }
            sys.stderr.write(json.dumps(payload, separators=(",", ":")) + "\n")
        else:
            phase = "resolving upload" if info["phase"] == "resolve" else "analyzing"
            typer.echo(f"… {phase} (elapsed {int(info['elapsed'])}s)", err=True)

    return _cb


def _wait_and_emit(
    runtime: RuntimeContext,
    *,
    asset_id: str | None = None,
    upload_id: str | None = None,
    interval: float,
    timeout: float,
    extra: dict[str, Any] | None = None,
) -> None:
    """Block until analysis completes, then emit the final status JSON."""
    with runtime.sdk_errors():
        status = runtime.get_client().wait_for_asset(
            asset_id=asset_id,
            upload_id=upload_id,
            interval=interval,
            timeout=timeout,
            on_poll=_poll_heartbeat(runtime),
        )
        result: dict[str, Any] = dict(extra or {})
        result.update(
            {
                "assetId": status.asset_id,
                "hasRunningJob": status.has_running_job,
                "lastUpdatedTime": status.last_updated_time,
            }
        )
        runtime.emit_result(result)


def asset_status(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    upload_id: Optional[str] = typer.Option(
        None, "--upload-id", help="Upload ID from `asset upload` (resolves to the asset)."
    ),
    wait: bool = typer.Option(False, "--wait", help="Poll until analysis completes."),
    interval: float = typer.Option(10.0, "--interval", help="Seconds between polls (with --wait)."),
    timeout: float = typer.Option(1800.0, "--timeout", help="Max seconds to wait (with --wait)."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Check asset processing status (by asset ID or upload ID; --wait to block)."""
    aid = (asset_id or asset or "").strip() or None
    if aid and upload_id:
        raise typer.BadParameter("Pass an asset ID or --upload-id, not both.")
    if not aid and not upload_id:
        raise typer.BadParameter("Missing ID. Pass an ASSET_ID argument, --asset, or --upload-id.")

    runtime: RuntimeContext = ctx.obj

    if upload_id or wait:
        if dry_run:
            runtime.emit_result(
                {
                    "dry_run": True,
                    "operation": "asset_status",
                    "asset_id": aid,
                    "upload_id": upload_id,
                    "wait": wait,
                }
            )
            return
        if wait:
            _wait_and_emit(
                runtime,
                asset_id=aid,
                upload_id=upload_id,
                interval=interval,
                timeout=timeout,
                extra={"uploadId": upload_id} if upload_id else None,
            )
            return
        # --upload-id without --wait: resolve once and report.
        with runtime.sdk_errors():
            info = runtime.get_client().resolve_upload(upload_id)
            resolved_id = getattr(info, "asset_id", None)
            runtime.emit_result(
                {
                    "uploadId": upload_id,
                    "assetId": resolved_id,
                    "uploaded": getattr(info, "uploaded", None),
                    "resolved": bool(resolved_id),
                }
            )
        return

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
    wait: bool = typer.Option(False, "--wait", help="Block until analysis completes."),
    interval: float = typer.Option(10.0, "--interval", help="Seconds between polls (with --wait)."),
    timeout: float = typer.Option(1800.0, "--timeout", help="Max seconds to wait (with --wait)."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Upload a single file as an asset (--wait blocks until analysis completes)."""
    from .. import render

    runtime: RuntimeContext = ctx.obj
    runtime.confirm_or_abort("write", yes=yes, dry_run=dry_run)
    if dry_run:
        runtime.emit_result(
            {"dry_run": True, "operation": "upload_asset", "path": str(path), "wait": wait}
        )
        return

    with runtime.sdk_errors():
        sdk = runtime.get_client()
        with render.status_spinner("Uploading…", enabled=not runtime.is_agent_mode):
            resp = sdk.upload_asset(path, name=name)
        upload_id = resp.asset.submit.upload_id
        display_name = name or path.name

        if wait:
            _wait_and_emit(
                runtime,
                upload_id=upload_id,
                interval=interval,
                timeout=timeout,
                extra={"uploadId": upload_id, "name": display_name},
            )
            return

        # Resolve once so callers get an assetId when it's already available;
        # a failure here must not mask the successful upload.
        asset_id: str | None = None
        uploaded: bool | None = None
        try:
            info = sdk.resolve_upload(upload_id)
            asset_id = getattr(info, "asset_id", None)
            uploaded = getattr(info, "uploaded", None)
        except Exception:
            pass
        runtime.emit_result(
            {
                "assetId": asset_id,
                "uploadId": upload_id,
                "name": display_name,
                "uploaded": uploaded,
            }
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
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
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
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
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
