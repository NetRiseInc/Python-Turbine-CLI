"""API tier: generated GraphQL ops plus catalog, schema, and raw GraphQL."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

from . import render
from .completion import complete_query_files
from .runtime import ExitCode, RuntimeContext

api_app = typer.Typer(help="Full GraphQL API — escape hatch when curated commands are not enough.")


@api_app.command("catalog")
def catalog(
    ctx: typer.Context,
    as_json: bool = typer.Option(False, "--json", help="Emit catalog as JSON."),
) -> None:
    """List available API operations (slim index)."""
    runtime: RuntimeContext = ctx.obj
    catalog_path = Path(__file__).resolve().parent / "_generated" / "catalog.json"
    if not catalog_path.exists():
        runtime.emit_error(ExitCode.USAGE, "Catalog not generated. Run make turbine-cli-generate.")
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    if as_json or runtime.is_agent_mode:
        sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    else:
        render.print_result(payload)


@api_app.command("graphql")
def graphql(
    ctx: typer.Context,
    query: Optional[str] = typer.Option(None, "--query", "-q", help="GraphQL query string."),
    query_file: Optional[Path] = typer.Option(
        None,
        "--query-file",
        help="Path to a .graphql file (- for stdin).",
        autocompletion=complete_query_files,
    ),
    variables: str = typer.Option("{}", "--variables", help="JSON variables object."),
    operation_name: Optional[str] = typer.Option(None, "--operation-name"),
) -> None:
    """Execute an arbitrary GraphQL query or mutation."""
    runtime: RuntimeContext = ctx.obj
    gql = query
    if query_file:
        gql = sys.stdin.read() if str(query_file) == "-" else query_file.read_text(encoding="utf-8")
    if not gql:
        runtime.emit_error(ExitCode.USAGE, "Provide --query or --query-file")
    try:
        vars_obj = json.loads(variables)
    except json.JSONDecodeError as exc:
        from .errors import format_json_error

        runtime.emit_error(ExitCode.USAGE, format_json_error(exc))
    if not runtime.is_agent_mode:
        render.print_graphql(gql)
    with runtime.sdk_errors():
        with render.status_spinner("Executing GraphQL…", enabled=not runtime.is_agent_mode):
            client = runtime.get_client().graphql()
            response = client.execute(
                query=gql,
                operation_name=operation_name,
                variables=vars_obj,
            )
            data = client.get_data(response)
        runtime.emit_result(data)


@api_app.command("schema")
def schema_show(
    ctx: typer.Context,
    schema_path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to schema.graphql (defaults to bundled copy if present).",
    ),
    type_name: Optional[str] = typer.Option(None, "--type", help="Filter to a single GraphQL type block."),
) -> None:
    """Print the GraphQL schema (optionally filtered to one type)."""
    runtime: RuntimeContext = ctx.obj
    path = schema_path or _default_schema_path()
    if not path or not path.exists():
        runtime.emit_error(ExitCode.USAGE, "Schema file not found. Pass --path.")
    text = path.read_text(encoding="utf-8")
    if type_name:
        text = _extract_type_block(text, type_name) or f"# Type {type_name} not found"
    if runtime.is_agent_mode:
        sys.stdout.write(text + "\n")
    else:
        render.print_graphql(text)


def _default_schema_path() -> Path | None:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[4] / "sdk-artifacts" / "schema.graphql",
        Path.cwd() / "sdk-artifacts" / "schema.graphql",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _extract_type_block(schema: str, type_name: str) -> str | None:
    import re

    pattern = rf"(type|input|enum|interface|union|scalar)\s+{re.escape(type_name)}\b[\s\S]*?(?=\n(?:type|input|enum|interface|union|scalar)\s+\w|\Z)"
    match = re.search(pattern, schema)
    return match.group(0).strip() if match else None
