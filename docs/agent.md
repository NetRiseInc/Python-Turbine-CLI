# Turbine CLI — Agent guide

Ultra-concise playbook for automation and LLM agents.

## Setup

CLI missing? `uv tool install netrise-turbine-cli` (or `pipx` / `pip`). `turbine skill install` places this skill in Cursor, Claude Code, Codex, and opencode skill directories.

If `turbine` isn't on `PATH` (common in sandboxes), it's in a project venv: use `poetry run turbine`, `uv run turbine`, `source .venv/bin/activate` first, or `./.venv/bin/turbine`. Isolated installs (`uv tool` / `pipx`) put `turbine` on `PATH` globally.

Env vars (or `.env`): prefer `TURBINE_ENDPOINT`, `TURBINE_AUDIENCE`, `TURBINE_DOMAIN`, `TURBINE_CLIENT_ID`, `TURBINE_CLIENT_SECRET`, `TURBINE_ORGANIZATION_ID` (unprefixed names still work).

```bash
turbine auth status -o json
```

## Loop

```bash
# 1. Discover — curated shortcuts + full API index
turbine api catalog --json -o json

# 2. Prefer curated resource commands
turbine asset list --limit 20 --fields id,name -o json
turbine vuln list ASSET_ID --detail lite --limit 50 -o json

# 3. Escape hatch — exact input schema for any GraphQL op
turbine api assets-relay --schema -o json
turbine api assets-relay --input '{"cursor":{"first":10}}' -o json
```

`--output` / `-o` works before or after the subcommand.

## Upload and analyze

Analysis takes minutes. `--wait` blocks (heartbeats on stderr, data on stdout):

```bash
turbine asset upload fw.bin --yes --wait -o json   # upload + wait, one command
```

Split flow: `asset upload` returns `uploadId` (`assetId` is null until the asset registers), then `turbine asset status --upload-id UPLOAD_ID --wait -o json` (drop `--wait` for a single check). Never scan `asset list` to find an upload. Afterwards: `turbine asset get ASSET_ID`, `turbine vuln list ASSET_ID`.

## Input

**Curated list commands:** `--asset`, `--group`, `--filter`, `--sort`, `--limit`, `--fields` (dot paths).

**API commands:** `--input '{"key":"value"}'` or `--input-file path.json` (use `-` for stdin); promoted kebab-case flags merge into the payload; `turbine api <cmd> --schema` for exact JSON Schema.

Placeholders: `ASSET_ID`, `GROUP_ID`, `CVE_ID`, `USER_ID` — substitute real IDs.

## Output contract

| Stream | Content |
| --- | --- |
| stdout | Data only — compact JSON; list commands stream NDJSON (one object per line) |
| stderr | Logs, spinners, human hints |

Exit codes: **0** ok · **2** usage · **3** GraphQL · **4** auth · **5** network

Errors are JSON on stderr in agent mode: `{"error":"…","code":2}` — never tracebacks.

## Token discipline

- Prefer curated commands: `asset list --detail summary`, `vuln list --detail lite`
- Always set `--limit` and `--fields` on list commands
- Use `api graphql` only when curated + generated ops are insufficient

## Safety

- Destructive ops require `--yes` in non-interactive mode
- Validate first with `--dry-run`

## Escape hatch

```bash
turbine api graphql -q 'query { … }' --variables '{}' -o json
turbine api schema --type QueryAsset -o json
```

## Curated vs api

| Need | Use |
| --- | --- |
| List assets, vulns, secrets, etc. | `turbine <resource> list` with `--detail` / `--limit` / `--fields` |
| Single record, upload, remediate | `turbine <resource> <verb>` |
| Obscure GraphQL op or custom input | `turbine api <operation>` |
| Ad-hoc GraphQL | `turbine api graphql` |

## Reference

- Command index: [reference.md](../reference.md)
- Cursor skill: [SKILL.md](../SKILL.md)
