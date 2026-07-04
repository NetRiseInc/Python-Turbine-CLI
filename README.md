# NetRise Turbine CLI

SDK-backed CLI for the Turbine platform — resource-oriented commands for everyday work, full GraphQL API as an escape hatch.

## Approach

Two tiers, one runtime:

| Tier | When to use | Example |
| --- | --- | --- |
| **Curated** (default) | Everyday tasks — list assets, remediate vulns, manage groups | `turbine asset list` |
| **`api`** | Full GraphQL coverage, custom inputs, new SDK ops | `turbine api assets-relay --schema` |

Same auth and output modes for both tiers; only rendering changes:

- **TTY** — Rich tables, panels, confirmation prompts
- **`--output json` or pipe** — compact JSON on stdout (NDJSON for lists), exit codes, no prompts

| Audience | Guide |
| --- | --- |
| Human operators | [docs/human.md](docs/human.md) — runnable examples |
| AI / automation | [docs/agent.md](docs/agent.md) — loop, I/O contract, token discipline |

## Install

Three tiers — pick how much you want:

| Tier | Command | You get |
| --- | --- | --- |
| SDK only | `pip install netrise-turbine-sdk` | Python SDK |
| SDK + CLI | `uv tool install netrise-turbine-cli` (or `pipx` / `pip`) | `turbine` command, SDK included |
| Everything | `turbine skill install` | Agent skill in Cursor, Claude Code, and Codex |

`turbine skill install` detects which agent tools you have (`~/.cursor`, `~/.claude`, `~/.agents`/`~/.codex`) and installs the bundled skill to each; use `--agent` / `--scope project` for explicit control and `turbine skill status` to inspect. Developing in this repo? `make turbine-cli-test` sets up the poetry env with the local SDK.

## Auth

Set credentials via `TURBINE_*` env vars (legacy unprefixed names still work) or `.env`:

`TURBINE_ENDPOINT` · `TURBINE_AUDIENCE` · `TURBINE_DOMAIN` · `TURBINE_CLIENT_ID` · `TURBINE_CLIENT_SECRET` · `TURBINE_ORGANIZATION_ID`

```bash
turbine auth status
turbine auth login --save   # verify + persist non-secrets to ~/.config/turbine/config.toml
```

## Command map

| Resource | Commands |
| --- | --- |
| `asset` | `list`, `get`, `upload`, `files`, `status`, `activity`, `hashes` |
| `vuln` | `list`, `get`, `overview`, `remediate` |
| `group` | `list`, `members`, `create`, `update`, `delete`, `add-assets`, `remove-assets` |
| `component` | `list`, `grouped`, `crypto` |
| `secret`, `credential`, `cert`, `key`, `misconfig`, `license`, `protection` | `list` |
| `user` | `list`, `invite`, `delete`, `remove` |
| `org` | `info`, `settings` |
| `search` | full-text search |
| `api` | all 114 GraphQL ops + `catalog`, `graphql`, `schema` |

## Quick start

Human — list assets (lite detail, default):

```bash
turbine asset list --limit 10
```

Agent — catalog then execute:

```bash
turbine api catalog --json
turbine asset list --dry-run -o json
turbine api assets-relay --schema -o json
```

`--output` / `-o` may appear before or after the subcommand.

## Documentation

| File | What |
| --- | --- |
| [docs/human.md](docs/human.md) | Human guide + per-command examples |
| [docs/agent.md](docs/agent.md) | Agent playbook |
| [reference.md](reference.md) | Generated API index + curated mapping |
| [SKILL.md](SKILL.md) | Cursor agent skill |

## Regenerate

From repo root:

```bash
make turbine-python-cli
```

Rebuilds API commands, catalog, coverage manifest, reference, SKILL auto-section, and human examples.

## Test

```bash
make turbine-cli-test
```
