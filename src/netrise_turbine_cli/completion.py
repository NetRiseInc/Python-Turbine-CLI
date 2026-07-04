"""Shell completion helpers."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import typer
from netrise_turbine_sdk import TurbineClient, TurbineClientConfig

CACHE_DIR = Path.home() / ".cache" / "turbine"
CACHE_FILE = CACHE_DIR / "completions.json"
CACHE_TTL_SECONDS = 300


def _load_cache() -> dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(data: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _refresh_asset_cache() -> dict[str, str]:
    cached = _load_cache()
    now = time.time()
    assets = cached.get("assets", {})
    if assets and now - cached.get("assets_ts", 0) < CACHE_TTL_SECONDS:
        return assets
    sdk = TurbineClient(TurbineClientConfig.from_env())
    try:
        mapping: dict[str, str] = {}
        for asset in sdk.iter_assets_relay_summary(page_size=200, max_pages=5):
            mapping[asset.id] = asset.name or asset.id
        cached["assets"] = mapping
        cached["assets_ts"] = now
        _save_cache(cached)
        return mapping
    finally:
        sdk.close()


def complete_asset_id(ctx: typer.Context, args: list[str], incomplete: str) -> list[str]:
    try:
        assets = _refresh_asset_cache()
        return [aid for aid in assets if aid.startswith(incomplete)][:50]
    except Exception:
        return []


def complete_query_files(ctx: typer.Context, args: list[str], incomplete: str) -> list[str]:
    candidates: list[str] = []
    for base in (Path.cwd(), Path.cwd() / "sdk-artifacts" / "queries"):
        if not base.exists():
            continue
        for path in base.glob("*.graphql"):
            s = str(path)
            if s.startswith(incomplete):
                candidates.append(s)
    return candidates[:50]
