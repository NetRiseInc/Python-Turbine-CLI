"""Rich rendering helpers for human-mode CLI output."""

from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Any, Iterator

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import install as install_rich_traceback

_console = Console(stderr=False)
_err_console = Console(stderr=True)

install_rich_traceback(show_locals=False, console=_err_console)


@contextmanager
def status_spinner(message: str, *, enabled: bool = True) -> Iterator[None]:
    if not enabled:
        yield
        return
    with _err_console.status(message):
        yield


def print_json_schema(schema: dict[str, Any]) -> None:
    text = json.dumps(schema, indent=2)
    _console.print(Syntax(text, "json", theme="monokai", word_wrap=True))


def print_result(data: Any) -> None:
    if isinstance(data, list) and data and isinstance(data[0], dict):
        _print_table(data)
        return
    if isinstance(data, dict):
        _console.print(Panel(json.dumps(data, indent=2, default=str), title="Result"))
        return
    _console.print(data)


def _print_table(rows: list[dict[str, Any]]) -> None:
    keys: list[str] = []
    for row in rows[:1]:
        keys = list(row.keys())[:8]
    if not keys:
        _console.print("No rows.")
        return
    table = Table(show_header=True, header_style="bold magenta")
    for key in keys:
        table.add_column(key)
    for row in rows[:200]:
        table.add_row(*[str(row.get(k, "")) for k in keys])
    _console.print(table)
    if len(rows) > 200:
        _err_console.print(f"[dim]Showing 200 of {len(rows)} rows. Use --output json for full output.[/dim]")


def print_error(message: str, *, details: Any = None) -> None:
    body = message
    if details is not None:
        body += f"\n\n{details}"
    _err_console.print(Panel(body, title="Error", border_style="red"))


def print_graphql(query: str) -> None:
    _console.print(Syntax(query, "graphql", theme="monokai", word_wrap=True))
