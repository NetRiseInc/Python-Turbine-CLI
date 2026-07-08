"""Extract the CLI commands advertised across the published docs.

The docs are the contract: every ``turbine …`` line inside a fenced bash
block is something we promise works. This module parses those lines (plus
the structured per-operation records in reference.md) so the test suite can
execute exactly what the docs advertise and fail with a pointer to the
offending doc file and line when the CLI drifts.
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path

CLI_ROOT = Path(__file__).resolve().parents[1]

# Docs whose fenced ```bash blocks contain runnable examples.
EXAMPLE_DOCS = ("README.md", "SKILL.md", "docs/human.md", "docs/agent.md")
REFERENCE_DOC = "reference.md"
ALL_DOCS = (*EXAMPLE_DOCS, REFERENCE_DOC)


@dataclass(frozen=True)
class DocCommand:
    """A single advertised `turbine …` invocation."""

    source: str
    line: int
    argv: tuple[str, ...]

    @property
    def text(self) -> str:
        return " ".join(self.argv)

    @property
    def test_id(self) -> str:
        return f"{self.source}:{self.line}:{self.text}"


@dataclass(frozen=True)
class ApiReference:
    """Structured claims for one `api <name>` operation in reference.md."""

    name: str
    line: int
    risk: str | None
    flags: tuple[str, ...]


def _parse_command_line(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not stripped.startswith("turbine "):
        return None
    try:
        # comments=True drops trailing `# …` annotations in the examples.
        tokens = shlex.split(stripped, comments=True, posix=True)
    except ValueError:
        return None
    if not tokens or tokens[0] != "turbine":
        return None
    return tuple(tokens)


def _bash_block_lines(text: str):
    """Yield (line_number, line) for lines inside fenced ```bash blocks."""
    in_block = False
    is_bash = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_block:
                in_block = False
                is_bash = False
            else:
                in_block = True
                is_bash = stripped[3:].strip() == "bash"
            continue
        if in_block and is_bash:
            yield lineno, line


_SCHEMA_LINE_RE = re.compile(r"\*\*Schema:\*\*\s+`(turbine [^`]+)`")


def extract_doc_commands() -> list[DocCommand]:
    """All runnable commands advertised in the docs, in document order."""
    commands: list[DocCommand] = []
    for rel in EXAMPLE_DOCS:
        text = (CLI_ROOT / rel).read_text(encoding="utf-8")
        for lineno, line in _bash_block_lines(text):
            argv = _parse_command_line(line)
            if argv:
                commands.append(DocCommand(rel, lineno, argv))
    # reference.md advertises a runnable `--schema` invocation per API op.
    text = (CLI_ROOT / REFERENCE_DOC).read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _SCHEMA_LINE_RE.search(line)
        if match:
            argv = _parse_command_line(match.group(1))
            if argv:
                commands.append(DocCommand(REFERENCE_DOC, lineno, argv))
    return commands


_SECTION_RE = re.compile(r"^### `api (?P<name>[a-z0-9-]+)`")


def extract_api_references() -> list[ApiReference]:
    """Per-operation Risk/Flags claims from reference.md."""
    text = (CLI_ROOT / REFERENCE_DOC).read_text(encoding="utf-8")
    refs: list[ApiReference] = []
    name: str | None = None
    start = 0
    risk: str | None = None
    flags: tuple[str, ...] = ()

    def flush() -> None:
        if name is not None:
            refs.append(ApiReference(name, start, risk, flags))

    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _SECTION_RE.match(line)
        if match:
            flush()
            name, start, risk, flags = match.group("name"), lineno, None, ()
        elif name is not None:
            if line.startswith("- **Risk:**"):
                risk = line.split("**Risk:**", 1)[1].strip()
            elif line.startswith("- **Flags:**"):
                flags = tuple(
                    f.strip() for f in line.split("**Flags:**", 1)[1].split(",") if f.strip()
                )
    flush()
    return refs


_INLINE_RE = re.compile(r"`(turbine(?: [^`]*)?)`")


def extract_mentioned_command_tokens() -> list[tuple[str, ...]]:
    """Token tuples for every `turbine …` mention (bash blocks + inline code).

    Inline mentions are often partial (``turbine api <operation> --schema``),
    so these are only suitable for coverage accounting, not execution.
    """
    mentions: list[tuple[str, ...]] = []
    for rel in ALL_DOCS:
        text = (CLI_ROOT / rel).read_text(encoding="utf-8")
        for match in _INLINE_RE.finditer(text):
            try:
                tokens = shlex.split(match.group(1), posix=True)
            except ValueError:
                tokens = match.group(1).split()
            if tokens and tokens[0] == "turbine":
                mentions.append(tuple(tokens))
        for _, line in _bash_block_lines(text):
            argv = _parse_command_line(line)
            if argv:
                mentions.append(argv)
    return mentions
