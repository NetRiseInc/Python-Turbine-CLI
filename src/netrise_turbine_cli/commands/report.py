"""Asset comparison report commands."""

from __future__ import annotations

import typer

APP_NAME = "report"
APP_HELP = "Asset comparison reports."


def register(app: typer.Typer) -> None:
    app.command("list")(list_reports)


def list_reports(ctx: typer.Context) -> None:
    """List asset comparison reports."""
    from ._common import run_graphql_by_name

    run_graphql_by_name(
        ctx,
        method_name="query_list_asset_comparison_reports",
        input_model_name="ListAssetComparisonReportsInput",
        input_param="list_asset_comparison_reports_args",
        payload={"cursor": {"first": 50}},
        risk="read",
    )
