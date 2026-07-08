"""User-friendly CLI error formatting."""

from __future__ import annotations

import json
import re
from collections.abc import Collection
from typing import Any

from pydantic import ValidationError


def format_validation_error(
    exc: ValidationError,
    *,
    flag_prefix: str = "--",
    known_flags: Collection[str] | None = None,
) -> str:
    """Map Pydantic validation errors to CLI-friendly messages.

    ``known_flags`` is the set of kebab-case option names the command actually
    exposes. Fields covered by a real flag are reported as ``--flag: msg``;
    everything else is reported as an input field with a ``--input`` hint, so
    we never suggest options that don't exist.
    """
    lines: list[str] = []
    needs_input_hint = False
    for err in exc.errors():
        loc = err.get("loc", ())
        msg = err.get("msg", "invalid value")
        flag = _loc_to_flag(loc, flag_prefix=flag_prefix)
        kebab = flag[len(flag_prefix):] if flag else None
        if flag and (known_flags is None or kebab in known_flags):
            lines.append(f"{flag}: {msg}")
        else:
            dotted = ".".join(str(x) for x in loc) or "input"
            lines.append(f'input field "{dotted}": {msg}')
            needs_input_hint = True
    text = "; ".join(lines) if lines else str(exc)
    if needs_input_hint:
        text += " — pass it via --input '<json>' (see --schema for the input shape)"
    return text


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
