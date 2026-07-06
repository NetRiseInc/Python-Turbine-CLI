"""Agent skill management: install the bundled SKILL.md for Cursor, Claude Code, Codex, or opencode."""

from __future__ import annotations

import hashlib
import shutil
from importlib import resources
from pathlib import Path
from typing import Optional

import typer

from ..runtime import ExitCode, RuntimeContext

APP_NAME = "skill"
APP_HELP = "Install the Turbine agent skill for Cursor, Claude Code, Codex, and opencode."

# Agent name -> (detection dirs in $HOME, user-scope skills dir, project-scope skills dir).
# `user` is relative to $HOME, `project` is relative to the current directory.
AGENTS: dict[str, dict[str, object]] = {
    "cursor": {
        "detect": [".cursor"],
        "user": ".cursor/skills",
        "project": ".cursor/skills",
    },
    "claude": {
        "detect": [".claude"],
        "user": ".claude/skills",
        "project": ".claude/skills",
    },
    "codex": {
        "detect": [".agents", ".codex"],
        "user": ".agents/skills",
        "project": ".agents/skills",
    },
    # opencode uses its own native dir (~/.config/opencode/skills, .opencode/skills);
    # it also reads the .claude and .agents locations above.
    "opencode": {
        "detect": [".config/opencode", ".opencode"],
        "user": ".config/opencode/skills",
        "project": ".opencode/skills",
    },
}


def register(app: typer.Typer) -> None:
    app.command("install")(install)
    app.command("uninstall")(uninstall)
    app.command("status")(status)


def packaged_skill_dir() -> Path:
    """Locate the self-contained skill bundled inside the package."""
    root = Path(str(resources.files("netrise_turbine_cli"))) / "_skill"
    candidates = [p for p in root.iterdir() if p.is_dir()] if root.is_dir() else []
    if not candidates:
        raise FileNotFoundError(
            "Packaged skill not found; this build of netrise-turbine-cli is missing _skill/."
        )
    return candidates[0]


def _dir_digest(path: Path) -> str:
    """Content hash of a directory tree (relative paths + file bytes)."""
    digest = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(file.relative_to(path)).encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()


def _skills_base(agent: str, scope: str) -> Path:
    base = Path.home() if scope == "user" else Path.cwd()
    return base / str(AGENTS[agent][scope])


def _detected_agents() -> list[str]:
    home = Path.home()
    return [
        name
        for name, spec in AGENTS.items()
        if any((home / d).is_dir() for d in spec["detect"])  # type: ignore[union-attr]
    ]


def _resolve_agents(runtime: RuntimeContext, agent: str, scope: str) -> list[str]:
    if agent != "all":
        if agent not in AGENTS:
            runtime.emit_error(
                ExitCode.USAGE,
                f"Unknown agent '{agent}'. Choose from: {', '.join(AGENTS)}, all.",
            )
        return [agent]
    if scope == "project":
        # Committing the skill to a repo serves every team member's tool.
        return list(AGENTS)
    detected = _detected_agents()
    if not detected:
        runtime.emit_error(
            ExitCode.USAGE,
            "No agent tools detected in your home directory "
            "(~/.cursor, ~/.claude, ~/.agents, ~/.codex, ~/.config/opencode). "
            "Use --agent cursor|claude|codex|opencode to install explicitly.",
        )
    return detected


def install(
    ctx: typer.Context,
    agent: str = typer.Option("all", "--agent", help="cursor, claude, codex, opencode, or all (detected)."),
    scope: str = typer.Option("user", "--scope", help="user (home dir) or project (current dir)."),
    force: bool = typer.Option(False, "--force", help="Overwrite a modified existing install."),
) -> None:
    """Install the bundled agent skill into each agent tool's skills directory."""
    runtime: RuntimeContext = ctx.obj
    if scope not in ("user", "project"):
        runtime.emit_error(ExitCode.USAGE, f"Unknown scope '{scope}'. Choose user or project.")
    try:
        source = packaged_skill_dir()
    except FileNotFoundError as exc:
        runtime.emit_error(ExitCode.USAGE, str(exc))
    source_digest = _dir_digest(source)

    results = []
    for name in _resolve_agents(runtime, agent, scope):
        dest = _skills_base(name, scope) / source.name
        if dest.exists():
            if _dir_digest(dest) == source_digest:
                results.append({"agent": name, "path": str(dest), "action": "up-to-date"})
                continue
            if not force:
                runtime.emit_error(
                    ExitCode.USAGE,
                    f"{dest} exists and differs from the packaged skill. "
                    "Re-run with --force to overwrite.",
                )
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest)
        results.append({"agent": name, "path": str(dest), "action": "installed"})
    runtime.emit_result({"skill": source.name, "scope": scope, "results": results})


def uninstall(
    ctx: typer.Context,
    agent: str = typer.Option("all", "--agent", help="cursor, claude, codex, opencode, or all (detected)."),
    scope: str = typer.Option("user", "--scope", help="user (home dir) or project (current dir)."),
) -> None:
    """Remove the installed agent skill."""
    runtime: RuntimeContext = ctx.obj
    if scope not in ("user", "project"):
        runtime.emit_error(ExitCode.USAGE, f"Unknown scope '{scope}'. Choose user or project.")
    try:
        skill_name = packaged_skill_dir().name
    except FileNotFoundError as exc:
        runtime.emit_error(ExitCode.USAGE, str(exc))

    agents = list(AGENTS) if agent == "all" else [agent]
    if agent != "all" and agent not in AGENTS:
        runtime.emit_error(
            ExitCode.USAGE, f"Unknown agent '{agent}'. Choose from: {', '.join(AGENTS)}, all."
        )
    results = []
    for name in agents:
        dest = _skills_base(name, scope) / skill_name
        if dest.exists():
            shutil.rmtree(dest)
            results.append({"agent": name, "path": str(dest), "action": "removed"})
        else:
            results.append({"agent": name, "path": str(dest), "action": "not-installed"})
    runtime.emit_result({"skill": skill_name, "scope": scope, "results": results})


def status(
    ctx: typer.Context,
    scope: str = typer.Option("user", "--scope", help="user (home dir) or project (current dir)."),
) -> None:
    """Show which agent tools are detected and where the skill is installed."""
    runtime: RuntimeContext = ctx.obj
    if scope not in ("user", "project"):
        runtime.emit_error(ExitCode.USAGE, f"Unknown scope '{scope}'. Choose user or project.")
    try:
        source = packaged_skill_dir()
    except FileNotFoundError as exc:
        runtime.emit_error(ExitCode.USAGE, str(exc))
    source_digest = _dir_digest(source)
    detected = set(_detected_agents())

    results = []
    for name in AGENTS:
        dest = _skills_base(name, scope) / source.name
        if not dest.exists():
            state = "not-installed"
        elif _dir_digest(dest) == source_digest:
            state = "installed"
        else:
            state = "modified"
        results.append(
            {
                "agent": name,
                "detected": name in detected,
                "path": str(dest),
                "state": state,
            }
        )
    runtime.emit_result({"skill": source.name, "scope": scope, "results": results})
