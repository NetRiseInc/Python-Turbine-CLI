"""Dot-path field projection for CLI output."""

from __future__ import annotations

from typing import Any


def project_fields(data: Any, fields: list[str], *, strict: bool = True) -> Any:
    """Project dot-path fields from nested dict/list data."""
    if not fields:
        return data
    if isinstance(data, list):
        return [project_fields(item, fields, strict=strict) for item in data]
    if not isinstance(data, dict):
        return data

    out: dict[str, Any] = {}
    missing: list[str] = []
    for field in fields:
        field = field.strip()
        if not field:
            continue
        value = _get_path(data, field.split("."))
        if value is _MISSING:
            missing.append(field)
            continue
        _set_path(out, field.split("."), value)

    if strict and missing:
        raise ValueError(f"Unknown field(s): {', '.join(missing)}")
    return out or data


class _MissingType:
    pass


_MISSING = _MissingType()


def _get_path(data: Any, parts: list[str]) -> Any:
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _set_path(target: dict[str, Any], parts: list[str], value: Any) -> None:
    current = target
    for part in parts[:-1]:
        nxt = current.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            current[part] = nxt
        current = nxt
    current[parts[-1]] = value
