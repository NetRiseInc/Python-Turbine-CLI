"""CLI unit and smoke tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CLI_ROOT = Path(__file__).resolve().parents[1]
SRC = CLI_ROOT / "src"
sys.path.insert(0, str(SRC))

from netrise_turbine_cli.errors import format_validation_error
from netrise_turbine_cli.fields import project_fields


def test_project_fields_dot_path() -> None:
    data = {"asset": {"id": "a1", "name": "fw"}, "score": 9}
    out = project_fields(data, ["asset.id", "score"])
    assert out == {"asset": {"id": "a1"}, "score": 9}


def test_project_fields_strict_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown field"):
        project_fields({"a": 1}, ["missing"], strict=True)


def test_format_validation_error() -> None:
    from pydantic import BaseModel, Field

    class M(BaseModel):
        asset_id: str = Field(alias="assetId")

    try:
        M.model_validate({})
    except Exception as exc:
        msg = format_validation_error(exc)  # type: ignore[arg-type]
        assert "asset" in msg.lower()


def _run_turbine(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [sys.executable, "-m", "netrise_turbine_cli.cli", *args],
        cwd=CLI_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_root_help() -> None:
    proc = _run_turbine(["--help"])
    assert proc.returncode == 0
    assert "asset" in proc.stdout
    assert "api" in proc.stdout


def test_asset_list_dry_run_json() -> None:
    proc = _run_turbine(["asset", "list", "--dry-run", "-o", "json"])
    assert proc.returncode == 0
    data = json.loads(proc.stdout.strip())
    assert data["dry_run"] is True
    assert data["operation"] == "iter_assets_relay_lite"


def test_output_flag_anywhere() -> None:
    proc = _run_turbine(["asset", "list", "--dry-run", "--output", "json"])
    assert proc.returncode == 0
    assert json.loads(proc.stdout.strip())["dry_run"] is True


def test_explicit_table_output_survives_pipe() -> None:
    """-o table must render a table even when stdout is piped (P0 bug)."""
    proc = _run_turbine(["asset", "list", "--dry-run", "-o", "table"])
    assert proc.returncode == 0
    with pytest.raises(json.JSONDecodeError):
        json.loads(proc.stdout.strip())
    assert "dry_run" in proc.stdout


def test_search_invocation_works() -> None:
    """The documented `turbine search <term>` form must work (P0 bug)."""
    proc = _run_turbine(["search", "router", "--dry-run", "-o", "json"])
    assert proc.returncode == 0
    data = json.loads(proc.stdout.strip())
    assert data["dry_run"] is True
    assert data["operation"] == "query_search"
    assert data["kwargs"]["search_args"]["query"] == "router"


def test_api_graphql_error_no_traceback() -> None:
    """api graphql must emit a structured error, never a traceback (P0 bug)."""
    env_overrides = {
        "TURBINE_ENDPOINT": "http://127.0.0.1:1/graphql",
        "TURBINE_DOMAIN": "http://127.0.0.1:1",
        "TURBINE_AUDIENCE": "http://127.0.0.1:1/",
        "TURBINE_CLIENT_ID": "x",
        "TURBINE_CLIENT_SECRET": "x",
        "TURBINE_ORGANIZATION_ID": "x",
    }
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env.update(env_overrides)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "netrise_turbine_cli.cli",
            "api",
            "graphql",
            "-q",
            "query { __typename }",
            "-o",
            "json",
        ],
        cwd=CLI_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode != 0
    assert "Traceback" not in proc.stderr
    assert "Traceback" not in proc.stdout
    payload = json.loads(proc.stderr.strip().splitlines()[-1])
    assert "error" in payload
    assert "code" in payload


def test_api_catalog_help() -> None:
    proc = _run_turbine(["api", "catalog", "--help"])
    assert proc.returncode == 0


def test_catalog_json_generated() -> None:
    catalog = SRC / "netrise_turbine_cli" / "_generated" / "catalog.json"
    data = json.loads(catalog.read_text(encoding="utf-8"))
    assert len(data) >= 100
    assert all(row["group"] == "api" for row in data)


def test_asset_get_requires_id() -> None:
    proc = _run_turbine(["asset", "get"])
    assert proc.returncode != 0
    assert "ASSET_ID" in proc.stderr or "Missing" in proc.stderr


def test_asset_get_dry_run_with_flag() -> None:
    proc = _run_turbine(["asset", "get", "--asset", "test-id", "--dry-run", "-o", "json"])
    assert proc.returncode == 0
    data = json.loads(proc.stdout.strip())
    assert data["dry_run"] is True


def test_asset_status_help_lists_wait_flags() -> None:
    proc = _run_turbine(["asset", "status", "--help"])
    assert proc.returncode == 0
    for flag in ("--upload-id", "--wait", "--interval", "--timeout"):
        assert flag in proc.stdout


def test_asset_status_rejects_both_ids() -> None:
    proc = _run_turbine(["asset", "status", "asset-1", "--upload-id", "up-1"])
    assert proc.returncode != 0
    assert "not both" in proc.stderr


def test_asset_status_requires_some_id() -> None:
    proc = _run_turbine(["asset", "status"])
    assert proc.returncode != 0
    assert "Missing ID" in proc.stderr


def test_asset_status_upload_id_dry_run() -> None:
    proc = _run_turbine(["asset", "status", "--upload-id", "up-1", "--dry-run", "-o", "json"])
    assert proc.returncode == 0
    data = json.loads(proc.stdout.strip())
    assert data == {
        "dry_run": True,
        "operation": "asset_status",
        "asset_id": None,
        "upload_id": "up-1",
        "wait": False,
    }


def test_asset_status_wait_dry_run() -> None:
    proc = _run_turbine(["asset", "status", "asset-1", "--wait", "--dry-run", "-o", "json"])
    assert proc.returncode == 0
    data = json.loads(proc.stdout.strip())
    assert data["wait"] is True
    assert data["asset_id"] == "asset-1"


def test_asset_upload_dry_run_reports_wait() -> None:
    proc = _run_turbine(
        ["asset", "upload", "fw.bin", "--wait", "--dry-run", "-o", "json"]
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout.strip())
    assert data["dry_run"] is True
    assert data["operation"] == "upload_asset"
    assert data["path"] == "fw.bin"
    assert data["wait"] is True


def test_load_cli_config_from_dotenv(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text('endpoint="https://example.test/graphql"\n', encoding="utf-8")
    from netrise_turbine_cli.config import load_cli_config

    import netrise_turbine_cli.config as config_mod

    config_mod._env_loaded = False
    monkeypatch.delenv("endpoint", raising=False)
    monkeypatch.delenv("TURBINE_ENDPOINT", raising=False)
    cfg = load_cli_config()
    assert cfg.endpoint == "https://example.test/graphql"


def test_coverage_manifest() -> None:
    coverage = SRC / "netrise_turbine_cli" / "_generated" / "coverage.json"
    data = json.loads(coverage.read_text(encoding="utf-8"))
    assert data["api_count"] >= 100
    assert len(data["curated"]) >= 25


# --- Tiered install: packaged skill and `turbine skill` commands ---


def _run_turbine_home(args: list[str], home: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["HOME"] = str(home)
    return subprocess.run(
        [sys.executable, "-m", "netrise_turbine_cli.cli", *args],
        cwd=CLI_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_packaged_skill_present_and_portable() -> None:
    """The wheel bundles a self-contained skill with no repo-relative links."""
    from netrise_turbine_cli.commands.skill import packaged_skill_dir

    skill_dir = packaged_skill_dir()
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert skill_md.startswith("---")
    assert "name:" in skill_md
    assert "docs/agent.md" not in skill_md  # rewritten to references/
    assert "](references/agent.md)" in skill_md
    assert (skill_dir / "references" / "agent.md").is_file()
    assert (skill_dir / "references" / "reference.md").is_file()
    assert (skill_dir / "agents" / "openai.yaml").is_file()


@pytest.mark.parametrize(
    ("agent", "base"),
    [
        ("cursor", ".cursor"),
        ("claude", ".claude"),
        ("codex", ".agents"),
        ("opencode", ".config/opencode"),
    ],
)
def test_skill_install_per_agent(tmp_path, agent, base) -> None:
    proc = _run_turbine_home(["-o", "json", "skill", "install", "--agent", agent], tmp_path)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout.strip())
    assert result["results"][0]["action"] == "installed"
    installed = tmp_path / base / "skills" / result["skill"] / "SKILL.md"
    assert installed.is_file()
    assert "](references/agent.md)" in installed.read_text(encoding="utf-8")


def test_skill_install_all_detects_and_force(tmp_path) -> None:
    (tmp_path / ".claude").mkdir()

    proc = _run_turbine_home(["-o", "json", "skill", "install"], tmp_path)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout.strip())
    assert [r["agent"] for r in result["results"]] == ["claude"]
    assert not (tmp_path / ".cursor").exists()
    assert not (tmp_path / ".agents").exists()

    proc = _run_turbine_home(["-o", "json", "skill", "status"], tmp_path)
    states = {r["agent"]: r["state"] for r in json.loads(proc.stdout.strip())["results"]}
    assert states == {
        "cursor": "not-installed",
        "claude": "installed",
        "codex": "not-installed",
        "opencode": "not-installed",
    }

    # Re-install on an unmodified copy is a no-op.
    proc = _run_turbine_home(["-o", "json", "skill", "install"], tmp_path)
    assert json.loads(proc.stdout.strip())["results"][0]["action"] == "up-to-date"

    # Modified copy: refuse without --force, overwrite with it.
    skill_name = result["skill"]
    installed_md = tmp_path / ".claude" / "skills" / skill_name / "SKILL.md"
    installed_md.write_text("local edits\n", encoding="utf-8")
    proc = _run_turbine_home(["-o", "json", "skill", "install"], tmp_path)
    assert proc.returncode == 2
    assert "force" in proc.stderr.lower()
    proc = _run_turbine_home(["-o", "json", "skill", "install", "--force"], tmp_path)
    assert proc.returncode == 0
    assert json.loads(proc.stdout.strip())["results"][0]["action"] == "installed"
    assert installed_md.read_text(encoding="utf-8") != "local edits\n"

    proc = _run_turbine_home(["-o", "json", "skill", "uninstall", "--agent", "claude"], tmp_path)
    assert proc.returncode == 0
    assert not installed_md.exists()


def test_skill_install_no_agents_detected(tmp_path) -> None:
    proc = _run_turbine_home(["-o", "json", "skill", "install"], tmp_path)
    assert proc.returncode == 2
    payload = json.loads(proc.stderr.strip().splitlines()[-1])
    assert "--agent" in payload["error"]


def test_version_matches_pyproject() -> None:
    """__version__ derives from package metadata, which mirrors pyproject.toml."""
    import netrise_turbine_cli

    pyproject = (CLI_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    declared = next(
        line.split('"')[1] for line in pyproject.splitlines() if line.startswith("version = ")
    )
    assert netrise_turbine_cli.__version__ == declared

    proc = _run_turbine(["--version"])
    assert proc.returncode == 0
    assert proc.stdout.strip() == declared


def test_pyproject_has_no_path_dependency() -> None:
    """A path dependency would make the CLI unpublishable to PyPI."""
    pyproject = (CLI_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    deps = pyproject.split("[tool.poetry.dependencies]")[1].split("[")[0]
    assert "path =" not in deps and "path=" not in deps
    assert "netrise-turbine-sdk" in deps


def _string_constants_in_commands(suffix: str) -> set[str]:
    """Collect string literals ending in *suffix* from curated command modules."""
    import ast

    found: set[str] = set()
    for path in (SRC / "netrise_turbine_cli" / "commands").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.endswith(suffix):
                    found.add(node.value)
    return found


def test_curated_input_model_names_exist() -> None:
    """Every *Input model name referenced by curated commands must exist in the SDK.

    Guards against typos like UserDeleteInput (real model: UserInput), which
    would raise AttributeError at runtime.
    """
    from netrise_turbine_sdk_graphql import input_types

    names = {n for n in _string_constants_in_commands("Input") if n[0].isupper()}
    assert names, "expected curated commands to reference input models"
    missing = sorted(n for n in names if not hasattr(input_types, n))
    assert not missing, f"input models not found in SDK: {missing}"


def test_curated_input_params_match_client_signature() -> None:
    """Every *_args param name referenced by curated commands must be accepted
    by some generated Client method."""
    import inspect

    from netrise_turbine_sdk_graphql.client import Client

    valid_params: set[str] = set()
    for _, fn in inspect.getmembers(Client, predicate=inspect.isfunction):
        valid_params.update(inspect.signature(fn).parameters)

    params = _string_constants_in_commands("_args")
    assert params, "expected curated commands to reference input params"
    unknown = sorted(p for p in params if p not in valid_params)
    assert not unknown, f"input params not accepted by any Client method: {unknown}"


def test_parse_json_option_rejects_malformed_json() -> None:
    import typer

    from netrise_turbine_cli.commands._common import parse_json_option

    assert parse_json_option(None, name="--filter") is None
    assert parse_json_option('{"severity": "CRITICAL"}', name="--filter") == {"severity": "CRITICAL"}
    assert parse_json_option("severity=CRITICAL", name="--filter") == {"severity": "CRITICAL"}
    # Malformed JSON containing '=' must raise, not be misparsed as key=value.
    with pytest.raises(typer.BadParameter):
        parse_json_option('{"key": "bad value', name="--filter")
