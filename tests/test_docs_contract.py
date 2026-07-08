"""Docs-driven contract tests: execute exactly what the docs advertise.

Tier 1 (always runs, offline): every documented `turbine …` command is
executed with `--dry-run` appended (or `--help` for the few commands that
cannot dry-run). A failure names the doc file and line that advertises the
broken command.

Tier 2 (opt-in, `TURBINE_CLI_DOCS_LIVE=1`): read-only commands run for real
against the live API using the resource IDs from `turbine/cli/.env`;
mutations stay `--dry-run` so nothing is ever written to the org.
"""

from __future__ import annotations

import enum
import json
import os
import subprocess
import sys
import typing
from functools import lru_cache
from pathlib import Path

import pytest

CLI_ROOT = Path(__file__).resolve().parents[1]
SRC = CLI_ROOT / "src"
sys.path.insert(0, str(SRC))

from _docs_manifest import (  # noqa: E402
    ApiReference,
    DocCommand,
    extract_api_references,
    extract_doc_commands,
    extract_mentioned_command_tokens,
)

LIVE = os.environ.get("TURBINE_CLI_DOCS_LIVE") == "1"

DOC_COMMANDS = extract_doc_commands()
API_REFERENCES = extract_api_references()


# --- Execution harness -------------------------------------------------------


_RESULT_CACHE: dict[tuple, subprocess.CompletedProcess[str]] = {}


def run_turbine(
    args: tuple[str, ...],
    *,
    timeout: int = 60,
    home: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run the CLI once per unique argv; identical invocations are cached."""
    key = (args, str(home) if home else None)
    if key in _RESULT_CACHE:
        return _RESULT_CACHE[key]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    # Wide, dumb terminal so rich help output doesn't wrap or truncate flags.
    env["COLUMNS"] = "300"
    env["TERM"] = "dumb"
    if home is not None:
        env["HOME"] = str(home)
    proc = subprocess.run(
        [sys.executable, "-m", "netrise_turbine_cli.cli", *args],
        cwd=CLI_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
    _RESULT_CACHE[key] = proc
    return proc


# --- Command classification --------------------------------------------------


@lru_cache(maxsize=1)
def catalog_by_name() -> dict[str, dict]:
    path = SRC / "netrise_turbine_cli" / "_generated" / "catalog.json"
    return {row["name"]: row for row in json.loads(path.read_text(encoding="utf-8"))}


@lru_cache(maxsize=1)
def registered_paths() -> frozenset[tuple[str, ...]]:
    """Every (group, command) path registered on the CLI."""
    import typer

    from netrise_turbine_cli.cli import app

    paths: set[tuple[str, ...]] = set()

    def walk(t: typer.Typer, prefix: tuple[str, ...]) -> None:
        for cmd in t.registered_commands:
            name = cmd.name or (cmd.callback.__name__.replace("_", "-") if cmd.callback else "")
            if name:
                paths.add((*prefix, name))
        for grp in t.registered_groups:
            name = grp.name or (grp.typer_instance.info.name if grp.typer_instance else None)
            if name and grp.typer_instance is not None:
                walk(grp.typer_instance, (*prefix, name))

    walk(app, ())
    return frozenset(paths)


def command_path(argv: tuple[str, ...]) -> tuple[str, ...]:
    """Map a documented argv to its registered command path."""
    tail = argv[1:]
    if len(tail) >= 2 and (tail[0], tail[1]) in registered_paths():
        return (tail[0], tail[1])
    if tail and (tail[0],) in registered_paths():
        return (tail[0],)
    return tuple(t for t in tail[:2] if not t.startswith("-"))


# Curated commands that perform writes (everything else curated is a read).
CURATED_WRITE_PATHS = {
    ("asset", "upload"),
    ("asset", "upload-dir"),
    ("asset", "submit"),
    ("asset", "update"),
    ("vuln", "remediate"),
    ("group", "create"),
    ("group", "update"),
    ("group", "delete"),
    ("group", "add-assets"),
    ("group", "remove-assets"),
    ("user", "invite"),
    ("user", "delete"),
    ("user", "remove"),
}

# Read commands that don't expose --dry-run: tier 1 validates their --help,
# tier 2 runs them live.
NO_DRY_RUN_READ_PATHS = {
    ("asset", "files"),
    ("org", "info"),
    ("org", "settings"),
    ("notification", "list"),
    ("report", "list"),
}

# Commands that work offline exactly as documented (no network, no creds).
OFFLINE_PATHS = {("api", "catalog"), ("api", "schema")}

# Commands needing a network/local-state round trip that tier 1 can only
# help-check: auth talks to the token endpoint, skill writes to $HOME,
# api graphql executes arbitrary GraphQL.
HELP_ONLY_GROUPS = {"auth", "skill"}


def command_risk(argv: tuple[str, ...]) -> str:
    path = command_path(argv)
    if path and path[0] == "api":
        if len(argv) > 2 and argv[2] in catalog_by_name():
            return catalog_by_name()[argv[2]]["risk"]
        return "read"  # catalog / schema / graphql doc examples are reads
    if path in CURATED_WRITE_PATHS:
        return "write"
    return "read"


# --- Placeholder substitution -------------------------------------------------

# Uppercase placeholders used across the docs (longest first so e.g.
# COMPOSED_ASSET_ID is replaced before its ASSET_ID substring).
PLACEHOLDERS = (
    "COMPOSED_ASSET_ID",
    "ASSET_ID",
    "GROUP_ID",
    "CVE_ID",
    "USER_ID",
    "UPLOAD_ID",
    "CONFIG_ID",
    "SECRET_ID",
)

DUMMY_VALUES = {
    "COMPOSED_ASSET_ID": "dummy-asset-id",
    "ASSET_ID": "dummy-asset-id",
    "GROUP_ID": "dummy-group-id",
    "CVE_ID": "CVE-2021-44228",
    "USER_ID": "dummy-user-id",
    "UPLOAD_ID": "dummy-upload-id",
    "CONFIG_ID": "dummy-config-id",
    "SECRET_ID": "dummy-secret-id",
    "search_term": "firmware",
}


def _annotation_types(annotation: object):
    """Flatten Optional/Union/list annotations to concrete types."""
    args = typing.get_args(annotation)
    if not args:
        yield annotation
        return
    for arg in args:
        yield from _annotation_types(arg)


def dummy_for_api_flag(api_name: str, flag: str | None) -> str:
    """Type-aware dummy for a VALUE placeholder on a promoted api flag.

    Enum-typed fields need a real member (a bare string fails validation),
    bools/ints need coercible literals.
    """
    fallback = "dummy-value"
    if flag is None or not flag.startswith("--"):
        return fallback
    entry = catalog_by_name().get(api_name)
    if not entry or not entry.get("input_model"):
        return fallback
    from netrise_turbine_sdk_graphql import input_types

    model_cls = getattr(input_types, entry["input_model"], None)
    if model_cls is None:
        return fallback
    field = model_cls.model_fields.get(flag[2:].replace("-", "_"))
    if field is None:
        return fallback
    for typ in _annotation_types(field.annotation):
        if isinstance(typ, type):
            if issubclass(typ, enum.Enum):
                return str(next(iter(typ)).value)
            if typ is bool:
                return "true"
            if typ is int:
                return "1"
            if typ is float:
                return "1.0"
    return fallback


def substitute(argv: tuple[str, ...], values: dict[str, str]) -> tuple[str, ...]:
    """Replace documented placeholders with concrete values."""
    out: list[str] = []
    for tok in argv:
        for key in PLACEHOLDERS:
            if key in tok:
                tok = tok.replace(key, values[key])
        if tok == "search_term":
            tok = values.get("search_term", "firmware")
        out.append(tok)
    # Generic VALUE placeholders: resolve per promoted-flag type on api ops.
    api_name = argv[2] if len(argv) > 2 and argv[1] == "api" else None
    for i, tok in enumerate(out):
        if tok == "VALUE" and api_name:
            flag = out[i - 1] if i > 0 else None
            out[i] = dummy_for_api_flag(api_name, flag)
        elif "VALUE" in tok:
            out[i] = tok.replace("VALUE", "dummy-value")
    return tuple(out)


# --- Tier 1: offline ----------------------------------------------------------


def tier1_invocation(cmd: DocCommand, tmp_paths: dict[str, str]) -> tuple[tuple[str, ...], str]:
    """Return (argv-to-run, mode) for the offline tier.

    mode is one of:
      "as-is"   — run the documented command unchanged (offline-safe)
      "dry-run" — documented command with --dry-run appended
      "help"    — command group's --help (network/local-state commands)
    """
    argv = substitute(cmd.argv, DUMMY_VALUES)
    tail = list(argv[1:])
    path = command_path(argv)

    if any(t in ("--help", "--version") for t in tail):
        return tuple(tail), "as-is"
    if "--schema" in tail or path in OFFLINE_PATHS:
        return tuple(tail), "as-is"
    if (path and path[0] in HELP_ONLY_GROUPS) or path == ("api", "graphql"):
        return (*path, "--help"), "help"
    if path in NO_DRY_RUN_READ_PATHS:
        return (*path, "--help"), "help"

    # Substitute example file/dir arguments with real temp paths so commands
    # that check the filesystem behave; nothing is uploaded under --dry-run.
    tail = [tmp_paths.get(t, t) for t in tail]
    if "--dry-run" not in tail:
        tail.append("--dry-run")
    return tuple(tail), "dry-run"


@pytest.fixture(scope="session")
def tmp_paths(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    """Concrete stand-ins for the file/dir literals used in doc examples."""
    base = tmp_path_factory.mktemp("docs-contract")
    fw = base / "fw.bin"
    fw.write_bytes(b"\x7fELF-docs-contract-dummy")
    fw_dir = base / "firmware-dir"
    fw_dir.mkdir()
    (fw_dir / "one.bin").write_bytes(b"\x7fELF-docs-contract-dummy")
    return {
        "fw.bin": str(fw),
        "firmware.bin": str(fw),
        "./firmware-dir": str(fw_dir),
    }


@pytest.mark.parametrize("cmd", DOC_COMMANDS, ids=lambda c: c.test_id)
def test_documented_command_offline(cmd: DocCommand, tmp_paths: dict[str, str]) -> None:
    args, mode = tier1_invocation(cmd, tmp_paths)
    proc = run_turbine(args)
    detail = (
        f"\nadvertised at {cmd.source}:{cmd.line}\n"
        f"  documented: {cmd.text}\n"
        f"  executed:   turbine {' '.join(args)}\n"
        f"  stdout: {proc.stdout[:2000]}\n"
        f"  stderr: {proc.stderr[:2000]}"
    )
    assert proc.returncode == 0, f"exit {proc.returncode}{detail}"
    assert "Traceback" not in proc.stderr, f"traceback leaked{detail}"
    assert "No such option" not in proc.stderr, f"unknown option{detail}"
    if mode == "dry-run":
        first_line = proc.stdout.strip().splitlines()[0]
        json.loads(first_line)


# --- reference.md flag claims -------------------------------------------------


@lru_cache(maxsize=1)
def _click_root():
    from typer.main import get_command

    from netrise_turbine_cli.cli import app

    return get_command(app)


def _registered_flags(path: tuple[str, ...]) -> set[str]:
    cmd = _click_root()
    for name in path:
        cmd = cmd.commands[name]
    flags: set[str] = set()
    for param in cmd.params:
        flags.update(o for o in param.opts if o.startswith("--"))
        flags.update(o for o in getattr(param, "secondary_opts", ()) if o.startswith("--"))
    return flags


@pytest.mark.parametrize(
    "ref",
    [r for r in API_REFERENCES if r.flags],
    ids=lambda r: f"api-{r.name}",
)
def test_reference_flags_exist(ref: ApiReference) -> None:
    """Every flag reference.md advertises must exist on the real command."""
    registered = _registered_flags(("api", ref.name))
    missing = [flag for flag in ref.flags if flag not in registered]
    assert not missing, (
        f"reference.md:{ref.line} advertises flags {missing} "
        f"that `turbine api {ref.name}` does not register"
    )


def test_org_settings_mutation_never_runs_live() -> None:
    """update-org-level-settings is a full-replace mutation: omitted toggles are
    disabled org-wide, wiping component/vulnerability results for the tenant.
    The live docs sweep must always append --dry-run to it."""
    assert catalog_by_name()["update-org-level-settings"]["risk"] != "read"
    documented = [
        cmd
        for cmd in DOC_COMMANDS
        if len(cmd.argv) > 2 and cmd.argv[1] == "api" and cmd.argv[2] == "update-org-level-settings"
    ]
    assert documented, "expected update-org-level-settings to be documented"
    for cmd in documented:
        args, mode, _ = tier2_invocation(cmd, {"__unresolved__": ""})
        if args is not None:
            assert mode == "dry-run", f"{cmd.test_id} would run live"
            assert "--dry-run" in args, f"{cmd.test_id} missing --dry-run"


def test_reference_covers_all_api_operations() -> None:
    """reference.md documents every generated api operation, and only those."""
    documented = {r.name for r in API_REFERENCES}
    generated = set(catalog_by_name())
    assert documented == generated, (
        f"missing from reference.md: {sorted(generated - documented)}; "
        f"stale in reference.md: {sorted(documented - generated)}"
    )


# --- Coverage guard: everything registered is documented -----------------------


def _mentioned_paths() -> set[tuple[str, ...]]:
    paths: set[tuple[str, ...]] = set()
    for tokens in extract_mentioned_command_tokens():
        tail = tokens[1:3]
        clean: list[str] = []
        for tok in tail:
            if tok.startswith("-") or tok.startswith("<") or not tok.islower():
                break
            clean.append(tok)
        for depth in (2, 1):
            candidate = tuple(clean[:depth])
            if candidate in registered_paths():
                paths.add(candidate)
                break
    # `api <operation>` placeholders advertise the whole generated tier;
    # reference.md's per-op sections make each one concrete.
    for ref in API_REFERENCES:
        if ("api", ref.name) in registered_paths():
            paths.add(("api", ref.name))
    return paths


def test_every_registered_command_is_documented() -> None:
    """The reverse contract: no registered command is undocumented."""
    missing = registered_paths() - _mentioned_paths()
    assert not missing, (
        "registered CLI commands not advertised anywhere in the docs: "
        f"{sorted(missing)}"
    )


# --- Tier 2: live -------------------------------------------------------------


def _load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def _first_string_for_keys(data: object, keys: set[str]) -> str | None:
    """Depth-first search a JSON payload for the first value under any key."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k in keys and isinstance(v, str) and v:
                return v
        for v in data.values():
            found = _first_string_for_keys(v, keys)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _first_string_for_keys(item, keys)
            if found:
                return found
    return None


@pytest.fixture(scope="session")
def live_values() -> dict[str, str]:
    """Placeholder → real-resource mapping for the live tier.

    Values come from turbine/cli/.env; GROUP_ID and the download file path
    are resolved once per session from the live org.
    """
    env = _load_dotenv(CLI_ROOT / ".env")
    values: dict[str, str] = dict(DUMMY_VALUES)
    unresolved: set[str] = {"UPLOAD_ID", "CONFIG_ID"}

    if env.get("ASSET_ID"):
        values["ASSET_ID"] = env["ASSET_ID"]
        values["COMPOSED_ASSET_ID"] = env.get("COMPOSED_ASSET_ID", env["ASSET_ID"])
    else:
        unresolved |= {"ASSET_ID", "COMPOSED_ASSET_ID"}
    if env.get("VULNERABILITY_ID"):
        values["CVE_ID"] = env["VULNERABILITY_ID"]
    else:
        unresolved.add("CVE_ID")
    if env.get("USER_ID"):
        values["USER_ID"] = env["USER_ID"]
    else:
        unresolved.add("USER_ID")
    if env.get("NAME"):
        values["search_term"] = env["NAME"]
    if env.get("RISE_AI_INSIGHTS_ASSET_ID"):
        values["RISE_AI_ASSET_ID"] = env["RISE_AI_INSIGHTS_ASSET_ID"]

    # GROUP_ID: look up the seed group by name.
    group_id = None
    proc = run_turbine(("group", "list", "--limit", "100", "-o", "json"), timeout=120)
    if proc.returncode == 0:
        wanted = env.get("ASSET_GROUP_NAME")
        first = None
        for line in proc.stdout.strip().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            first = first or row.get("id")
            if wanted and row.get("name") == wanted:
                group_id = row.get("id")
                break
        group_id = group_id or first
    if group_id:
        values["GROUP_ID"] = group_id
    else:
        unresolved.add("GROUP_ID")

    # A real file path inside the seed asset, for download-file examples.
    file_path = None
    if "ASSET_ID" not in unresolved:
        proc = run_turbine(("asset", "files", values["ASSET_ID"], "-o", "json"), timeout=180)
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                payload = json.loads(proc.stdout.strip().splitlines()[0])
            except json.JSONDecodeError:
                payload = None
            file_path = _first_string_for_keys(payload, {"path", "filePath", "file_path"})
    if file_path:
        values["./path/to/file"] = file_path

    # A real secret ID from the seed asset, when it has secrets.
    secret_id = None
    if "ASSET_ID" not in unresolved:
        proc = run_turbine(
            ("secret", "list", values["ASSET_ID"], "--limit", "1", "-o", "json"), timeout=120
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                row = json.loads(proc.stdout.strip().splitlines()[0])
            except json.JSONDecodeError:
                row = None
            secret_id = _first_string_for_keys(row, {"id"})
    if secret_id:
        values["SECRET_ID"] = secret_id
    else:
        unresolved.add("SECRET_ID")

    values["__unresolved__"] = ",".join(sorted(unresolved))
    return values


def _live_substitute(
    cmd: DocCommand, values: dict[str, str]
) -> tuple[tuple[str, ...] | None, str]:
    """Return (argv, skip_reason). argv is None when the command must skip."""
    unresolved = set(values.get("__unresolved__", "").split(","))
    used = {p for p in PLACEHOLDERS for tok in cmd.argv if p in tok}
    blocked = used & unresolved
    if blocked:
        return None, f"placeholder(s) {sorted(blocked)} have no live value"
    argv = substitute(cmd.argv, values)
    if "./path/to/file" in values:
        argv = tuple(t.replace("./path/to/file", values["./path/to/file"]) for t in argv)
    elif any("./path/to/file" in t for t in argv):
        return None, "no file path resolvable from the seed asset"
    if any("VALUE" in t or "dummy-value" in t for t in argv):
        return None, "generic VALUE placeholder has no live value"
    return argv, ""


# Documented read ops that currently fail server-side regardless of input.
# Verified live; tracked as API issues, not CLI drift.
LIVE_SERVER_LIMITATIONS = {
    "caas-availability": "server returns null for non-nullable Query.caasAvailability",
    "rise-ai-analysis-data": "server rejects revision 0 assets (revision_id must be > 0)",
    "user-orgs": "requires a user token; client-credentials tokens have no user context",
}

# RISE AI features are only enabled for a dedicated seed asset.
RISE_AI_OPS_PREFIXES = ("rise-ai", "caas", "submit-rise-ai")


def tier2_invocation(
    cmd: DocCommand, values: dict[str, str]
) -> tuple[tuple[str, ...] | None, str, str]:
    """Return (argv-to-run, mode, skip_reason) for the live tier."""
    path = command_path(cmd.argv)
    tail_text = cmd.text

    if any(t in ("--help", "--version") for t in cmd.argv):
        return None, "", "help/version examples are covered offline"
    if "--schema" in cmd.argv or path in OFFLINE_PATHS:
        return None, "", "offline command, covered by tier 1"
    if path and path[0] == "skill":
        return None, "", "skill commands are local-only, covered by dedicated tests"
    if path == ("auth", "login"):
        return None, "", "auth login writes local config; auth status covers live auth"

    if path == ("api", "graphql"):
        # The documented query body is a placeholder; run the canonical
        # minimal query through the documented invocation shape.
        argv = tuple(
            "query { __typename }" if ("query {" in t or "…" in t) else t for t in cmd.argv[1:]
        )
        return argv, "live", ""

    api_name = cmd.argv[2] if len(cmd.argv) > 2 and cmd.argv[1] == "api" else None
    if api_name in LIVE_SERVER_LIMITATIONS and command_risk(cmd.argv) == "read":
        return None, "", f"known server limitation: {LIVE_SERVER_LIMITATIONS[api_name]}"

    if api_name and api_name.startswith(RISE_AI_OPS_PREFIXES) and "RISE_AI_ASSET_ID" in values:
        values = {**values, "ASSET_ID": values["RISE_AI_ASSET_ID"]}

    argv, reason = _live_substitute(cmd, values)
    if argv is None:
        return None, "", reason

    tail = list(argv[1:])
    risk = command_risk(cmd.argv)
    if risk != "read":
        if "--dry-run" not in tail:
            tail.append("--dry-run")
        return tuple(tail), "dry-run", ""
    if "--wait" in tail:
        return None, "", f"--wait blocks on analysis; not suitable for the sweep: {tail_text}"
    return tuple(tail), "live", ""


@pytest.mark.skipif(not LIVE, reason="set TURBINE_CLI_DOCS_LIVE=1 to run the live docs sweep")
@pytest.mark.parametrize("cmd", DOC_COMMANDS, ids=lambda c: c.test_id)
def test_documented_command_live(
    cmd: DocCommand, live_values: dict[str, str], tmp_paths: dict[str, str]
) -> None:
    args, mode, reason = tier2_invocation(cmd, live_values)
    if args is None:
        pytest.skip(reason)
    args = tuple(tmp_paths.get(t, t) for t in args)
    proc = run_turbine(args, timeout=300)
    detail = (
        f"\nadvertised at {cmd.source}:{cmd.line}\n"
        f"  documented: {cmd.text}\n"
        f"  executed:   turbine {' '.join(args)}\n"
        f"  stdout: {proc.stdout[:2000]}\n"
        f"  stderr: {proc.stderr[:2000]}"
    )
    assert proc.returncode == 0, f"exit {proc.returncode}{detail}"
    assert "Traceback" not in proc.stderr, f"traceback leaked{detail}"
    # Output contract: stdout is data only — JSON, one object per line (NDJSON
    # for lists). Empty stdout is a valid empty list.
    for line in proc.stdout.strip().splitlines():
        if line:
            json.loads(line)
