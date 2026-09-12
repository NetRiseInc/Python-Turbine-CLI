---
name: turbine-cli
description: Query and mutate the NetRise Turbine platform (assets, vulnerabilities, SBOMs, secrets, remediation) via the `turbine` CLI. Use when the user asks to inspect firmware or asset analysis results, run Turbine GraphQL operations, or automate Turbine workflows.
---

# Turbine CLI

## When to use

Use this skill when the user asks about Turbine assets, firmware analysis, vulnerabilities, SBOMs, secrets, remediation, or GraphQL automation against the Turbine API.

Full I/O contract and workflows: [docs/agent.md](docs/agent.md).

## Setup

Install if missing: `uv tool install netrise-turbine-cli` (or `pipx` / `pip`). This skill ships inside the CLI — `turbine skill install` places it in Cursor, Claude Code, Codex, and opencode; `turbine skill status` shows where.

If bare `turbine` is not on `PATH` (common in sandboxes), invoke through the project env:

- Poetry: `poetry run turbine …`
- uv: `uv run turbine …`
- Plain venv: `source .venv/bin/activate` or `./.venv/bin/turbine …`
- Isolated install (`uv tool` / `pipx`): `turbine` is global

Confirm with `turbine --version`.

Env (or `.env`): prefer `TURBINE_ENDPOINT`, `TURBINE_AUDIENCE`, `TURBINE_DOMAIN`, `TURBINE_CLIENT_ID`, `TURBINE_CLIENT_SECRET`, `TURBINE_ORGANIZATION_ID`.

Verify: `turbine auth status`

## Core loop

1. `turbine api catalog --json -o json` — API index with curated aliases.
2. Curated first: `turbine asset list --limit 20 --fields id,name -o json`
3. Escape hatch: `turbine api <operation> --schema -o json` then `--input '<json>'`
4. Raw GraphQL: `turbine api graphql -q '<graphql>' --variables '<json>'`

`--output` / `-o` may appear before or after the subcommand.

## Routing

| User says | Run |
| --- | --- |
| "last/latest asset I uploaded" | `turbine asset risk --latest` or `turbine asset list --sort createdAt:desc --limit 1` |
| "risk", "posture", "findings", "issues" | `turbine asset risk ASSET_ID` |
| "CVEs", "vulnerabilities", "exploits" | `turbine vuln list ASSET_ID --detail lite` |
| "misconfigurations", "hardening" | `turbine misconfig list ASSET_ID` |
| "secrets", "passwords", "credentials" | `turbine secret list ASSET_ID` / `turbine credential list ASSET_ID` |
| "certificates", "keys", "crypto" | `turbine cert list ASSET_ID` / `turbine key list ASSET_ID` |
| "licenses", "legal" | `turbine license list ASSET_ID` |
| "components", "SBOM", "dependencies" | `turbine component list ASSET_ID` |
| upload / analyze | `turbine asset upload fw.bin --yes --wait -o json` |

For broad "risk" questions, run `turbine asset risk` once, present counts, then ask which category to open — do not fan out across every list command. Details in [docs/agent.md](docs/agent.md).

## Quick rules

- Pass bare `ASSET_ID` (never `id|revision`); the CLI strips revision suffixes from output.
- Prefer curated lists with `--detail summary|lite` and `--limit` / `--fields`.
- Destructive commands need `--yes` in agent mode; dry-run first with `--dry-run`.
- stdout = data (NDJSON for lists); stderr = logs; errors are JSON on stderr.

<!-- AUTO-GENERATED-CLI-SECTION:START -->

## Generated API index

**168** API operations (regenerated from the SDK).

Start with curated commands (`turbine asset list`, `turbine vuln remediate`, …).
Use `turbine api <operation>` when you need an op the curated surface misses.

| API command | Risk | Curated alias |
| --- | --- | --- |
| `add-asset-groups-to-assets` | write | — |
| `add-assets-to-asset-group` | write | group add-assets |
| `add-security-group-member` | write | — |
| `asset-add-dependency` | write | — |
| `asset-modify-dependency` | write | — |
| `asset-remove-dependencies` | write | — |
| `asset-submit` | write | asset submit |
| `asset-update` | write | asset update |
| `bulk-delete-ac-rs` | write | — |
| `create-acr` | write | — |
| `create-asset-comparison-report` | write | — |
| `create-asset-group` | write | group create |
| `create-custom-role` | write | — |
| `create-notification-configuration` | write | — |
| `create-security-group` | write | — |
| `delete-acr` | destructive | — |
| `delete-asset-comparison-report` | destructive | — |
| `delete-asset-group` | destructive | group delete |
| `delete-custom-role` | destructive | — |
| `delete-notification-configuration` | destructive | — |
| `delete-security-group` | destructive | — |
| `invite-user` | write | — |
| `jira-integration-add-connected-space` | write | — |
| `jira-integration-create-issue` | write | — |
| `jira-integration-delete-connected-space` | write | — |
| `jira-integration-disconnect` | write | — |
| `jira-integration-reconnect` | write | — |
| `jira-integration-set-status-mapping-auto-sync` | write | — |
| `jira-integration-setup-action` | write | — |
| `jira-integration-test-connection` | write | — |
| `notify-notification-configuration` | write | — |
| `remediate-all-asset-vulnerabilities` | destructive | vuln remediate --all |
| `remediate-asset-vulnerabilities` | destructive | vuln remediate --bulk |
| `remediate-asset-vulnerability` | destructive | vuln remediate |
| `remediate-certificates` | destructive | — |
| `remediate-license-issues` | destructive | — |
| `remediate-private-keys` | destructive | — |
| `remediate-public-keys` | destructive | — |
| `remediate-secrets` | destructive | — |
| `remove-all-asset-groups-from-assets` | destructive | — |
| … | … | … |

See [reference.md](reference.md) for all 168 API operations.

<!-- AUTO-GENERATED-CLI-SECTION:END -->

## Reference

- Agent playbook: [docs/agent.md](docs/agent.md)
- Full command catalog: [reference.md](reference.md)
