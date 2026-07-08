"""Runtime helpers: client, I/O modes, errors, safety guards."""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import httpx
import typer
from netrise_turbine_sdk import TurbineClient, TurbineClientConfig
from netrise_turbine_sdk_graphql.exceptions import (
    GraphQLClientError,
    GraphQLClientGraphQLError,
    GraphQLClientGraphQLMultiError,
    GraphQLClientHttpError,
)
from pydantic import ValidationError

from . import render
from .config import load_cli_config
from .errors import format_json_error, format_validation_error
from .fields import project_fields

OutputMode = Literal["auto", "json", "table"]
RiskLevel = Literal["read", "write", "destructive"]


class ExitCode(int, Enum):
    OK = 0
    USAGE = 2
    GRAPHQL = 3
    AUTH = 4
    NETWORK = 5


@dataclass
class RuntimeContext:
    output: OutputMode = "auto"
    endpoint: str | None = None
    org: str | None = None
    _client: TurbineClient | None = None

    @property
    def effective_output(self) -> Literal["json", "table"]:
        # An explicit choice (flag, or flag hoisted into TURBINE_OUTPUT by the
        # argv pre-parser) always wins; only "auto" falls back to TTY detection.
        explicit = self.output
        if explicit == "auto":
            explicit = os.environ.get("TURBINE_OUTPUT", "").lower()
        if explicit in ("json", "table"):
            return explicit  # type: ignore[return-value]
        return "table" if sys.stdout.isatty() else "json"

    @property
    def is_agent_mode(self) -> bool:
        return self.effective_output == "json"

    def get_client(self) -> TurbineClient:
        if self._client is None:
            try:
                cfg = load_cli_config()
            except ValueError as exc:
                self.emit_error(ExitCode.USAGE, str(exc))
            sdk_cfg = cfg.to_sdk_config()
            if self.endpoint:
                sdk_cfg = TurbineClientConfig(
                    endpoint=self.endpoint,
                    audience=sdk_cfg.audience,
                    domain=sdk_cfg.domain,
                    client_id=sdk_cfg.client_id,
                    client_secret=sdk_cfg.client_secret,
                    organization_id=self.org or sdk_cfg.organization_id,
                    turbine_api_token=sdk_cfg.turbine_api_token,
                )
            elif self.org:
                sdk_cfg = TurbineClientConfig(
                    endpoint=sdk_cfg.endpoint,
                    audience=sdk_cfg.audience,
                    domain=sdk_cfg.domain,
                    client_id=sdk_cfg.client_id,
                    client_secret=sdk_cfg.client_secret,
                    organization_id=self.org,
                    turbine_api_token=sdk_cfg.turbine_api_token,
                )
            self._client = TurbineClient(sdk_cfg)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def load_input_payload(
        self,
        input_json: str | None,
        input_file: Path | None,
    ) -> dict[str, Any]:
        try:
            if input_json:
                return json.loads(input_json)
            if input_file:
                text = sys.stdin.read() if str(input_file) == "-" else input_file.read_text(encoding="utf-8")
                return json.loads(text) if text.strip() else {}
            return {}
        except json.JSONDecodeError as exc:
            self.emit_error(ExitCode.USAGE, format_json_error(exc))

    def emit_schema(self, model_cls: type) -> None:
        schema = model_cls.model_json_schema()
        if self.is_agent_mode:
            self._write_json(schema)
        else:
            render.print_json_schema(schema)

    def emit_result(self, result: Any, *, fields: list[str] | None = None) -> None:
        data = _to_jsonable(result)
        if fields:
            try:
                data = project_fields(data, fields, strict=True)
            except ValueError as exc:
                self.emit_error(ExitCode.USAGE, str(exc))
        if self.is_agent_mode:
            self._write_json(data)
        else:
            render.print_result(data)

    def emit_stream(
        self,
        iterator: Iterator[Any],
        *,
        fields: list[str] | None = None,
        limit: int | None = None,
        stream_ndjson: bool = True,
    ) -> None:
        """Emit iterator results; NDJSON in agent mode, table batch in human mode."""
        if self.is_agent_mode and stream_ndjson:
            count = 0
            for item in iterator:
                data = _to_jsonable(item)
                if fields:
                    try:
                        data = project_fields(data, fields, strict=True)
                    except ValueError as exc:
                        self.emit_error(ExitCode.USAGE, str(exc))
                sys.stdout.write(json.dumps(data, separators=(",", ":"), default=str) + "\n")
                count += 1
                if limit is not None and count >= limit:
                    break
            return

        items = self.iter_to_list(iterator, max_items=limit, fields=fields)
        self.emit_result(items)

    def emit_error(self, code: ExitCode, message: str, details: Any = None) -> None:
        if self.is_agent_mode:
            payload = {"error": message, "code": int(code)}
            if details is not None:
                payload["details"] = details
            sys.stderr.write(json.dumps(payload, separators=(",", ":"), default=str) + "\n")
        else:
            render.print_error(message, details=details)
        raise typer.Exit(code=int(code))

    @contextmanager
    def sdk_errors(self) -> Iterator[None]:
        """Map SDK and transport exceptions to the CLI error contract.

        Everything raised inside the block becomes a structured emit_error
        (message + exit code) instead of a raw traceback.
        """
        try:
            yield
        except ValidationError as exc:
            self.emit_error(ExitCode.USAGE, format_validation_error(exc))
        except GraphQLClientGraphQLMultiError as exc:
            self.emit_error(ExitCode.GRAPHQL, str(exc), details=exc.errors)
        except GraphQLClientGraphQLError as exc:
            self.emit_error(ExitCode.GRAPHQL, str(exc))
        except GraphQLClientHttpError as exc:
            code = ExitCode.AUTH if exc.status_code in {401, 403} else ExitCode.NETWORK
            self.emit_error(code, f"HTTP {exc.status_code}", details=str(exc))
        except GraphQLClientError as exc:
            self.emit_error(ExitCode.GRAPHQL, str(exc))
        except httpx.HTTPError as exc:
            self.emit_error(ExitCode.NETWORK, str(exc))
        except typer.Exit:
            raise
        except Exception as exc:
            self.emit_error(ExitCode.USAGE, str(exc))

    def confirm_or_abort(self, risk: RiskLevel, *, yes: bool, dry_run: bool) -> None:
        if dry_run or risk == "read" or yes:
            return
        if self.is_agent_mode:
            self.emit_error(ExitCode.USAGE, f"Operation requires --yes (risk={risk})")
        if not typer.confirm(f"This is a {risk} operation. Continue?", default=False):
            raise typer.Exit(code=int(ExitCode.USAGE))

    def run_graphql_op(
        self,
        *,
        op_name: str,
        method_name: str,
        kwargs: dict[str, Any],
        risk: RiskLevel,
        dry_run: bool,
        yes: bool,
    ) -> None:
        self.confirm_or_abort(risk, yes=yes, dry_run=dry_run)
        if dry_run:
            self.emit_result({"dry_run": True, "operation": op_name, "kwargs": _to_jsonable(kwargs)})
            return
        with self.sdk_errors():
            with render.status_spinner(f"Running {op_name}…", enabled=not self.is_agent_mode):
                client = self.get_client()
                method = getattr(client.graphql(), method_name)
                result = method(**kwargs)
            self.emit_result(result)

    def run_curated_op(
        self,
        *,
        op_name: str,
        method_name: str,
        call: Callable[[TurbineClient], Any],
        risk: RiskLevel,
        dry_run: bool,
        yes: bool,
    ) -> None:
        self.confirm_or_abort(risk, yes=yes, dry_run=dry_run)
        if dry_run:
            self.emit_result({"dry_run": True, "operation": op_name})
            return
        with self.sdk_errors():
            with render.status_spinner(f"Running {op_name}…", enabled=not self.is_agent_mode):
                result = call(self.get_client())
            self.emit_result(result)

    def iter_to_list(
        self,
        iterator: Iterator[Any],
        *,
        max_items: int | None,
        fields: list[str] | None,
    ) -> list[Any]:
        items: list[Any] = []
        for item in iterator:
            data = _to_jsonable(item)
            if fields:
                try:
                    data = project_fields(data, fields, strict=True)
                except ValueError as exc:
                    self.emit_error(ExitCode.USAGE, str(exc))
            items.append(data)
            if max_items is not None and len(items) >= max_items:
                break
        return items

    def _write_json(self, data: Any) -> None:
        sys.stdout.write(json.dumps(data, separators=(",", ":"), default=str) + "\n")


# Field names whose values may carry the API's internal composed asset ID
# shape ("<id>|<revision>"). The suffix is an implementation detail users
# should never see; every input surface accepts the bare ID.
_COMPOSED_ID_KEYS = frozenset({"composedAssetId", "composed_asset_id", "assetId", "asset_id"})

_COMPOSED_ID_RE = re.compile(r"^(.+)\|\d+$")


def _strip_composed_suffix(value: Any) -> Any:
    if isinstance(value, str):
        match = _COMPOSED_ID_RE.match(value)
        if match:
            return match.group(1)
    return value


def _to_jsonable(value: Any, *, key: str | None = None) -> Any:
    if hasattr(value, "model_dump"):
        return _to_jsonable(value.model_dump(mode="json", by_alias=True), key=key)
    if isinstance(value, list):
        return [_to_jsonable(v, key=key) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v, key=k) for k, v in value.items()}
    if key in _COMPOSED_ID_KEYS:
        return _strip_composed_suffix(value)
    return value
