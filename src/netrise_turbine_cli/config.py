"""CLI configuration: env vars, optional config file, profiles."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv
from netrise_turbine_sdk import TurbineClientConfig

CONFIG_DIR = Path.home() / ".config" / "turbine"
CONFIG_FILE = CONFIG_DIR / "config.toml"
_env_loaded = False


@dataclass(frozen=True)
class CliConfig:
    endpoint: str
    domain: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    audience: str | None = None
    organization_id: str | None = None
    turbine_api_token: str | None = None
    output: str | None = None

    def to_sdk_config(self) -> TurbineClientConfig:
        return TurbineClientConfig(
            endpoint=self.endpoint,
            domain=self.domain,
            client_id=self.client_id,
            client_secret=self.client_secret,
            audience=self.audience,
            organization_id=self.organization_id,
            turbine_api_token=self.turbine_api_token,
        )


def _env(name: str, *, prefixed: bool = True) -> str | None:
    keys = [f"TURBINE_{name.upper()}"] if prefixed else []
    keys.append(name)
    for key in keys:
        value = os.getenv(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _ensure_env_loaded() -> None:
    """Load .env from cwd or parent dirs (once per process)."""
    global _env_loaded
    if _env_loaded:
        return
    current_dir_env = Path.cwd() / ".env"
    if current_dir_env.exists():
        load_dotenv(current_dir_env, override=False)
    else:
        dotenv_path = find_dotenv(usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path, override=False)
        else:
            load_dotenv(override=False)
    _env_loaded = True


def load_cli_config(*, load_env_file: bool = True) -> CliConfig:
    """Load CLI config from env (TURBINE_* with legacy fallback) and optional config file."""
    if load_env_file:
        _ensure_env_loaded()

    file_values = _load_config_file()
    endpoint = _env("endpoint") or file_values.get("endpoint") or ""
    if not endpoint:
        raise ValueError(
            "endpoint is required. Set TURBINE_ENDPOINT or endpoint in the environment "
            "or .env file (e.g. https://apollo.turbine.netrise.io/graphql/v3)"
        )

    return CliConfig(
        endpoint=endpoint,
        domain=_env("domain") or file_values.get("domain"),
        client_id=_env("client_id") or file_values.get("client_id"),
        client_secret=_env("client_secret") or file_values.get("client_secret"),
        audience=_env("audience") or file_values.get("audience"),
        organization_id=_env("organization_id") or file_values.get("organization_id"),
        turbine_api_token=_env("api_token") or os.getenv("TURBINE_API_TOKEN"),
        output=_env("output") or file_values.get("output"),
    )


def save_cli_config(values: dict[str, Any]) -> Path:
    """Persist non-secret defaults to ~/.config/turbine/config.toml."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for key, value in values.items():
        if value is None:
            continue
        if key in {"client_secret", "turbine_api_token"}:
            continue
        lines.append(f'{key} = "{value}"')
    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return CONFIG_FILE


def _load_config_file() -> dict[str, str]:
    if not CONFIG_FILE.exists():
        return {}
    values: dict[str, str] = {}
    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw = line.split("=", 1)
        values[key.strip()] = raw.strip().strip('"').strip("'")
    return values
