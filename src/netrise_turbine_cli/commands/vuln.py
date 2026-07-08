"""Vulnerability resource commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ._common import FILTER_HELP, SORT_HELP, resolve_asset_id, run_graphql_by_name, run_list
from ._registry import VULN_LIST_METHODS

APP_NAME = "vuln"
APP_HELP = "Vulnerabilities: list, inspect, and remediate."


def register(app: typer.Typer) -> None:
    app.command("list")(list_vulns)
    app.command("get")(get_vuln)
    app.command("overview")(vuln_overview)
    app.command("remediate")(remediate_vuln)


def list_vulns(
    ctx: typer.Context,
    asset_id: Optional[str] = typer.Argument(None, help="Asset ID (or use --asset)."),
    asset: Optional[str] = typer.Option(None, "--asset", help="Asset ID."),
    detail: str = typer.Option("lite", "--detail", help="lite|full|detailed|detailed-lite"),
    filter_json: Optional[str] = typer.Option(None, "--filter", help=FILTER_HELP),
    sort_json: Optional[str] = typer.Option(None, "--sort", help=SORT_HELP),
    limit: int = typer.Option(100, "--limit"),
    all_pages: bool = typer.Option(False, "--all"),
    page_size: int = typer.Option(100, "--page-size"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List vulnerabilities for an asset."""
    aid = resolve_asset_id(asset_id, asset=asset)
    method = VULN_LIST_METHODS.get(detail, VULN_LIST_METHODS["lite"])
    run_list(
        ctx,
        method_name=method,
        asset_id=aid,
        filter_json=filter_json,
        sort_json=sort_json,
        limit=limit,
        all_pages=all_pages,
        page_size=page_size,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def get_vuln(
    ctx: typer.Context,
    vuln_id: Optional[str] = typer.Argument(None, help="Vulnerability ID (or use --id)."),
    vuln: Optional[str] = typer.Option(None, "--id", help="Vulnerability ID."),
    detail: str = typer.Option("full", "--detail", help="full|lite"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Get a single vulnerability."""
    vid = (vuln_id or vuln or "").strip()
    if not vid:
        raise typer.BadParameter("Missing vulnerability ID. Pass it as an argument or --id.")
    method = "query_vulnerability_lite" if detail == "lite" else "query_vulnerability"
    # Both operations take vulnerability_args: VulnerabilityInput.
    model = "VulnerabilityInput"
    param = "vulnerability_args"
    run_graphql_by_name(
        ctx,
        method_name=method,
        input_model_name=model,
        input_param=param,
        payload={"id": vid},
        risk="read",
        dry_run=dry_run,
    )


def vuln_overview(
    ctx: typer.Context,
    filter_json: Optional[str] = typer.Option(None, "--filter", help=FILTER_HELP),
    sort_json: Optional[str] = typer.Option(None, "--sort", help=SORT_HELP),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List vulnerability overview records across the org."""
    run_list(
        ctx,
        method_name="iter_vulnerabilities_overview",
        filter_json=filter_json,
        sort_json=sort_json,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def remediate_vuln(
    ctx: typer.Context,
    asset_id: str = typer.Option(..., "--asset", help="Asset ID."),
    input_json: Optional[str] = typer.Option(None, "--input", "-i"),
    input_file: Optional[Path] = typer.Option(None, "--input-file"),
    bulk: bool = typer.Option(False, "--bulk", help="Remediate multiple vulnerabilities."),
    all_vulns: bool = typer.Option(False, "--all", help="Remediate all vulnerabilities on asset."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Remediate one or more vulnerabilities (VEX)."""
    from ..runtime import RuntimeContext

    runtime: RuntimeContext = ctx.obj
    payload = runtime.load_input_payload(input_json, input_file)
    payload["assetId"] = asset_id
    if all_vulns:
        method = "mutation_remediate_all_asset_vulnerabilities"
        model = "CreateAllAssetVulnerabilitiesRemediationInput"
        param = "remediate_all_asset_vulnerabilities_args"
    elif bulk:
        method = "mutation_remediate_asset_vulnerabilities"
        model = "CreateAssetVulnerabilityRemediationsInput"
        param = "remediate_asset_vulnerabilities_args"
    else:
        method = "mutation_remediate_asset_vulnerability"
        model = "CreateAssetVulnerabilityRemediationInput"
        param = "remediate_asset_vulnerability_args"
    run_graphql_by_name(
        ctx,
        method_name=method,
        input_model_name=model,
        input_param=param,
        payload=payload,
        risk="destructive",
        dry_run=dry_run,
        yes=yes,
    )
