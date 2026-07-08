---
name: turbine-cli
description: Query and mutate the NetRise Turbine platform (assets, vulnerabilities, SBOMs, secrets, remediation) via the `turbine` CLI. Use when the user asks to inspect firmware or asset analysis results, run Turbine GraphQL operations, or automate Turbine workflows.
---

# Turbine CLI

## Setup

Install the CLI if missing: `uv tool install netrise-turbine-cli` (or `pipx` / `pip`). This skill ships inside the CLI — `turbine skill install` places it in Cursor, Claude Code, Codex, and opencode; `turbine skill status` shows where.

**Finding the `turbine` command.** If a bare `turbine` isn't on `PATH` (common in sandboxed agents), it's installed in a project virtualenv — invoke it through the env manager instead of assuming a global binary:

- Poetry project: `poetry run turbine …`
- uv project: `uv run turbine …`
- Plain venv: activate first (`source .venv/bin/activate`) or call `./.venv/bin/turbine …`
- Isolated install (`uv tool install` / `pipx`): `turbine` is global; no venv needed.

Confirm with `turbine --version` (or `poetry run turbine --version`).

Requires env (or `.env`): prefer `TURBINE_ENDPOINT`, `TURBINE_AUDIENCE`, `TURBINE_DOMAIN`, `TURBINE_CLIENT_ID`, `TURBINE_CLIENT_SECRET`, `TURBINE_ORGANIZATION_ID`.

Verify: `turbine auth status`

Full agent playbook: [docs/agent.md](docs/agent.md)

## Core loop (agents)

1. `turbine api catalog --json -o json` — API index with curated aliases.
2. Prefer curated: `turbine asset list --limit 20 --fields id,name -o json`
3. Escape hatch: `turbine api <operation> --schema -o json` then `--input '<json>'`
4. Raw GraphQL: `turbine api graphql -q '<graphql>' --variables '<json>'`

`--output` / `-o` may appear before or after the subcommand.

## Common workflows

**Upload and analyze (most common).** Analysis takes several minutes; `--wait` blocks and prints heartbeats to stderr:

```bash
# One command: upload, wait for analysis, get the asset ID
turbine asset upload fw.bin --yes --wait -o json
# → {"uploadId":"…","name":"fw.bin","assetId":"…","hasRunningJob":false,…}
```

Or split (upload now, check later): `asset upload` returns an `uploadId` (`assetId` may be null at first — the asset registers asynchronously), then:

```bash
turbine asset status --upload-id UPLOAD_ID --wait -o json   # blocks until done
turbine asset status --upload-id UPLOAD_ID -o json          # single non-blocking check
```

When done, fetch results: `turbine asset get ASSET_ID`, `turbine vuln list ASSET_ID --detail lite -o json`. Do not poll `asset list` to find the upload — `asset status --upload-id` is the direct path.

## Vague asks — route, summarize, then offer drill-downs

"Risk" in Turbine spans several finding categories: vulnerabilities (CVEs), exploit exposure, misconfigurations, secrets and credentials, certificates and keys, and license issues. When the user asks broadly — "what risk does this asset have?", "how bad is it?", "any security issues?", "what did the scan find?" — do NOT fan out across every list command. Run the one-call summary:

```bash
turbine asset risk ASSET_ID -o json     # risk score + counts per category
turbine asset risk --latest -o json     # most recently created asset ("the asset I just uploaded")
```

Each category in the output includes its `drillDown` command. Present the score and the non-zero counts, then ask which category to explore, e.g.: "Which type of risk are you interested in — CVEs, misconfigurations, certificate issues, detected secrets, license issues?" Only drill down immediately when the request names a category or one category obviously dominates.

Routing for specific phrases:

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

## Asset IDs

Some operations name their input `composedAssetId` — it is interchangeable with the plain asset ID. Always pass the bare `ASSET_ID` (never an `id|revision` value); the CLI strips any `|<revision>` suffix from output, so IDs you read back are always safe to reuse.

## Token discipline

- Prefer curated list commands with `--detail summary|lite` and `--limit` / `--fields`.
- List output is NDJSON in agent mode (one JSON object per line).
- Use `api graphql` only when necessary.

## Sort and filter

- `--sort FIELD[:asc|desc]`, e.g. `--sort createdAt:desc`. Case-insensitive field names; no `--sort-by`/`--sort-order` flags exist. Invalid fields error with the valid field list.
- `--filter` takes resource-specific JSON, e.g. `--filter '{"fields":[{"fieldName":"NAME","value":["router"],"operation":"CONTAINS"}]}'`. Exact shape: `turbine api <operation> --schema -o json`.

## Safety

- Destructive commands require `--yes` in agent mode.
- Dry-run first: `--dry-run`.

## Output contract

- stdout = data only (compact JSON; NDJSON for lists).
- stderr = logs, spinners, human hints.
- Exit codes: 0 ok, 2 usage, 3 GraphQL, 4 auth, 5 network.
- Errors: `{"error":"…","code":N}` on stderr — no tracebacks.

<!-- AUTO-GENERATED-CLI-SECTION:START -->

## Generated API index

Total API operations: **114** (regenerated from SDK).

Use curated commands first (`turbine asset list`, `turbine vuln remediate`, …).
Fall back to `turbine api <operation>` for full GraphQL coverage.

| API command | Risk | Curated alias |
| --- | --- | --- |
| `add-asset-groups-to-assets` | write | — |
| `add-assets-to-asset-group` | write | group add-assets |
| `asset-add-dependency` | write | — |
| `asset-modify-dependency` | write | — |
| `asset-remove-dependencies` | write | — |
| `asset-submit` | write | asset submit |
| `asset-update` | write | asset update |
| `create-asset-comparison-report` | write | — |
| `create-asset-group` | write | group create |
| `create-notification-configuration` | write | — |
| `delete-asset-comparison-report` | destructive | — |
| `delete-asset-group` | destructive | group delete |
| `delete-notification-configuration` | destructive | — |
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
| `remove-assets-from-asset-group` | destructive | group remove-assets |
| `set-asset-groups-to-asset` | write | — |
| `set-assets-to-asset-group` | write | — |
| `submit-rise-ai-analysis` | write | — |
| `update-asset-group` | write | group update |
| `update-notification-configuration` | write | — |
| `update-org-level-settings` | write | — |
| `user-action` | write | — |
| `user-delete` | destructive | user delete |
| `user-invite` | write | user invite |
| `user-remove` | destructive | user remove |
| `user-reset-password` | write | — |
| `user-set-user-role` | write | — |
| `user-update-user` | write | — |
| `activity` | read | — |
| `analytics` | read | — |
| `asset` | read | asset get |
| … | … | … |

See [reference.md](reference.md) for all 114 API operations.

<!-- AUTO-GENERATED-CLI-SECTION:END -->

## Reference

- Agent playbook: [docs/agent.md](docs/agent.md)
- Full command catalog: [reference.md](reference.md)
