"""User-friendly CLI error formatting."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError


def format_validation_error(exc: ValidationError, *, flag_prefix: str = "--") -> str:
    """Map Pydantic validation errors to CLI-friendly messages."""
    lines: list[str] = []
    for err in exc.errors():
        loc = err.get("loc", ())
        msg = err.get("msg", "invalid value")
        field = _loc_to_flag(loc, flag_prefix=flag_prefix)
        if field:
            lines.append(f"{field}: {msg}")
        else:
            lines.append(f"{'.'.join(str(x) for x in loc)}: {msg}")
    return "; ".join(lines) if lines else str(exc)


def format_json_error(exc: json.JSONDecodeError) -> str:
    return f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"


def _loc_to_flag(loc: tuple[Any, ...], *, flag_prefix: str) -> str | None:
    if not loc:
        return None
    head = loc[0]
    if not isinstance(head, str):
        return None
    return f"{flag_prefix}{_to_kebab(head)}"


def _to_kebab(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    return s.replace("_", "-").lower()
