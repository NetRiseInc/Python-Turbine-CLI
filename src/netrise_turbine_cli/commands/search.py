"""Search commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ..runtime import RuntimeContext
from ._common import run_graphql_by_name

APP_NAME = "search"
APP_HELP = "Cross-asset search."


def register(app: typer.Typer) -> None:
    app.command()(search)


def search(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query."),
    artifacts: Optional[str] = typer.Option(
        None, "--artifacts", help="Comma-separated artifact names (default: all)."
    ),
    input_json: Optional[str] = typer.Option(None, "--input", "-i"),
    input_file: Optional[Path] = typer.Option(None, "--input-file"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Search assets and artifacts."""
    runtime: RuntimeContext = ctx.obj
    payload = runtime.load_input_payload(input_json, input_file)
    payload["query"] = query
    if artifacts:
        payload["artifacts"] = [a.strip().upper() for a in artifacts.split(",") if a.strip()]
    elif "artifacts" not in payload:
        from netrise_turbine_sdk_graphql.enums import ArtifactName

        payload["artifacts"] = [a.value for a in ArtifactName]
    run_graphql_by_name(
        ctx,
        method_name="query_search",
        input_model_name="SearchInput",
        input_param="search_args",
        payload=payload,
        risk="read",
        dry_run=dry_run,
    )
