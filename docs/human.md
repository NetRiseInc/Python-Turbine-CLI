# Turbine CLI — Human guide

Resource-oriented commands for everyday Turbine operations. Use `turbine api` when you need the full GraphQL surface.

## Install

`uv tool install netrise-turbine-cli` (or `pipx` / `pip`) — the SDK comes with it. Using Cursor, Claude Code, or Codex? `turbine skill install` adds the Turbine agent skill to each tool it detects (`turbine skill status` to check).

## Auth

```bash
turbine auth status
turbine auth login --save
```

## Common patterns

**Get an asset ID first** — most per-asset commands need `ASSET_ID` from `asset list`:

```bash
turbine asset list --detail lite --limit 5 --fields id,name
# Copy the id column value, then:
turbine asset get ASSET_ID
turbine asset files ASSET_ID
turbine vuln list ASSET_ID --detail lite --limit 50
```

You can pass the ID positionally (`turbine asset get ASSET_ID`) or as a flag (`turbine asset get --asset ASSET_ID`).

**"What risk does this asset have?"** — one call summarizes every finding category (vulnerabilities, misconfigurations, secrets, certificates/keys, license issues) with drill-down commands:

```bash
turbine asset risk ASSET_ID
turbine asset risk --latest    # most recently created asset
```

**List with pagination and projection:**

```bash
turbine asset list --detail lite --limit 20 --fields id,name,status
turbine vuln list ASSET_ID --detail lite --limit 50
turbine secret list ASSET_ID --limit 100
```

**Sort and filter.** `--sort` takes `FIELD[:asc|desc]` — field names are case-insensitive (`createdAt`, `created_at`, and `CREATEDAT` all work):

```bash
turbine asset list --limit 10 --sort createdAt:desc --fields id,name,createdAt
turbine asset list --sort riskScore:desc --limit 10
```

An invalid field name errors with the full list of valid fields for that resource. `--filter` takes resource-specific filter JSON (see `turbine api <operation> --schema` for the exact shape) or a simple `key=value` shorthand:

```bash
turbine asset list --filter '{"fields":[{"fieldName":"NAME","value":["router"],"operation":"CONTAINS"}]}'
```

**Detail levels** replace the old `-lite`/`-summary`/`-relay` command variants:

| Resource | `--detail` values |
| --- | --- |
| `asset list` | `summary`, `lite` (default), `full`, `overview` |
| `vuln list` | `lite` (default), `full`, `detailed`, `detailed-lite` |
| `component list` | `lite` (default), `full` |
| `misconfig list` | `lite` (default), `full` |
| `key list` | `--type private` (default) or `public` |

**Mutations** support `--dry-run` and `--yes`. **Upload:** `turbine asset upload` / `upload-dir`. **API escape hatch:** `turbine api catalog`, `turbine api <operation> --schema`.

See [reference.md](../reference.md) for all API operations.

<!-- AUTO-GENERATED-HUMAN-EXAMPLES:START -->

## Curated commands

#### asset activity
Curated: asset activity
```bash
turbine asset activity ASSET_ID
```

#### asset files
Curated: asset files
```bash
turbine asset files ASSET_ID
```

#### asset get
Curated: asset get
```bash
turbine asset get ASSET_ID
```

#### asset hashes
Curated: asset hashes
```bash
turbine asset hashes ASSET_ID
```

#### asset list --detail full
Curated: asset list --detail full
```bash
turbine asset list --detail full --limit 20
```

#### asset list --detail lite
Curated: asset list --detail lite
```bash
turbine asset list --detail lite --limit 20 --fields id,name,status
```

#### asset list --detail overview
Curated: asset list --detail overview
```bash
turbine asset list --detail overview --limit 20
```

#### asset list --detail summary
Curated: asset list --detail summary
```bash
turbine asset list --detail summary --limit 20
```

#### asset risk
Curated: asset risk
```bash
turbine asset risk ASSET_ID
```

#### asset status
Curated: asset status
```bash
turbine asset status ASSET_ID
```

#### asset submit
Curated: asset submit
```bash
turbine asset submit --name my-example
```

#### asset update
Curated: asset update
```bash
turbine asset update --id ASSET_ID
```

#### asset upload
Curated: asset upload
```bash
turbine asset upload firmware.bin --name my-firmware
```

#### asset upload-dir
Curated: asset upload-dir
```bash
turbine asset upload-dir ./firmware-dir
```

#### auth login
Curated: auth login
```bash
turbine auth login --save
```

#### auth status
Curated: auth status
```bash
turbine auth status
```

#### cert list
Curated: cert list
```bash
turbine cert list ASSET_ID --limit 50
```

#### component crypto
Curated: component crypto
```bash
turbine component crypto ASSET_ID
```

#### component grouped
Curated: component grouped
```bash
turbine component grouped ASSET_ID
```

#### component list --detail full
Curated: component list --detail full
```bash
turbine component list ASSET_ID --detail full
```

#### component list --detail lite
Curated: component list --detail lite
```bash
turbine component list ASSET_ID --detail lite
```

#### credential list
Curated: credential list
```bash
turbine credential list ASSET_ID
```

#### group add-assets
Curated: group add-assets
```bash
turbine group add-assets --id GROUP_ID --input '{"assetIds":["ASSET_ID"]}'
```

#### group create
Curated: group create
```bash
turbine group create --name my-group --description 'Example group'
```

#### group delete
Curated: group delete
```bash
turbine group delete GROUP_ID
```

#### group list
Curated: group list
```bash
turbine group list --limit 20
```

#### group members
Curated: group members
```bash
turbine group members GROUP_ID
```

#### group remove-assets
Curated: group remove-assets
```bash
turbine group remove-assets --id GROUP_ID --input '{"assetIds":["ASSET_ID"]}'
```

#### group update
Curated: group update
```bash
turbine group update --id GROUP_ID --name renamed-group
```

#### key list --type private
Curated: key list --type private
```bash
turbine key list ASSET_ID --type private
```

#### key list --type public
Curated: key list --type public
```bash
turbine key list ASSET_ID --type public
```

#### license list
Curated: license list
```bash
turbine license list ASSET_ID
```

#### misconfig list --detail full
Curated: misconfig list --detail full
```bash
turbine misconfig list ASSET_ID --detail full
```

#### misconfig list --detail lite
Curated: misconfig list --detail lite
```bash
turbine misconfig list ASSET_ID --detail lite
```

#### notification list
Curated: notification list
```bash
turbine notification list
```

#### org info
Curated: org info
```bash
turbine org info
```

#### org settings
Curated: org settings
```bash
turbine org settings
```

#### protection list
Curated: protection list
```bash
turbine protection list ASSET_ID
```

#### report list
Curated: report list
```bash
turbine report list
```

#### search
Curated: search
```bash
turbine search search_term
```

#### secret list
Curated: secret list
```bash
turbine secret list ASSET_ID --limit 50
```

#### user delete
Curated: user delete
```bash
turbine user delete USER_ID --dry-run
```

#### user invite
Curated: user invite
```bash
turbine user invite --email user@example.com --role MEMBER
```

#### user list
Curated: user list
```bash
turbine user list --limit 20
```

#### user remove
Curated: user remove
```bash
turbine user remove USER_ID --dry-run
```

#### vuln get
Curated: vuln get
```bash
turbine vuln get CVE_ID
```

#### vuln get --detail lite
Curated: vuln get --detail lite
```bash
turbine vuln get CVE_ID --detail lite
```

#### vuln list --detail detailed
Curated: vuln list --detail detailed
```bash
turbine vuln list ASSET_ID --detail detailed
```

#### vuln list --detail detailed-lite
Curated: vuln list --detail detailed-lite
```bash
turbine vuln list ASSET_ID --detail detailed-lite
```

#### vuln list --detail full
Curated: vuln list --detail full
```bash
turbine vuln list ASSET_ID --detail full
```

#### vuln list --detail lite
Curated: vuln list --detail lite
```bash
turbine vuln list ASSET_ID --detail lite --limit 50
```

#### vuln overview
Curated: vuln overview
```bash
turbine vuln overview --limit 20
```

#### vuln remediate
Curated: vuln remediate
```bash
turbine vuln remediate --asset ASSET_ID --input '{"remediationId":{"vulnerabilityId":"CVE_ID"},"status":"NOT_AFFECTED","justification":"CODE_NOT_PRESENT"}' --dry-run
```

#### vuln remediate --all
Curated: vuln remediate --all
```bash
turbine vuln remediate --asset ASSET_ID --all --input '{"vulnerabilityFilter":{},"status":"NOT_AFFECTED","justification":"CODE_NOT_PRESENT"}' --dry-run
```

#### vuln remediate --bulk
Curated: vuln remediate --bulk
```bash
turbine vuln remediate --asset ASSET_ID --bulk --input '{"remediationIds":[{"vulnerabilityId":"CVE_ID"}],"status":"NOT_AFFECTED","justification":"CODE_NOT_PRESENT"}' --dry-run
```

## API operations

#### api activity
Retrieve a comprehensive log of actions and events for assets.
```bash
turbine api activity --asset-id ASSET_ID
```

#### api analytics
Access high-level risk data and charts for organization dashboards.
```bash
turbine api analytics
```

#### api asset-group-analytics
View risk metrics and exploit counts for a specific group.
```bash
turbine api asset-group-analytics --group-id GROUP_ID
```

#### api asset-group-members
List all assets associated with a specific asset group container.
```bash
turbine api asset-group-members --input '{"group_id":"GROUP_ID","cursor":{"first":10}}'
```

#### api asset-groups
Retrieve a detailed paginated list of all asset groups available.
```bash
turbine api asset-groups --input '{"cursor":{"first":10}}'
```

#### api asset-upload
Obtain a secure pre-signed URL to upload files for analysis.
```bash
turbine api asset-upload --upload-id UPLOAD_ID
```

#### api asset-vulnerability-remediation
Retrieve current VEX status and justification for a specific vulnerability.
```bash
turbine api asset-vulnerability-remediation --asset-id ASSET_ID --remediation-id VALUE --vulnerability-id CVE_ID
```

#### api assets-overview
View high-level risk and threat exposure metrics for multiple assets.
```bash
turbine api assets-overview --input '{"cursor":{"first":10}}'
```

#### api assets-relay
Retrieve a paginated, sortable list of assets with filtering options.
```bash
turbine api assets-relay --input '{"cursor":{"first":10}}'
```

#### api assets-relay-lite
Retrieve assets with trimmed fields — keeps identity, status, risk score, and analytic rollups; drops filesystems, SHA-256, exploit trees, and credential counts.
```bash
turbine api assets-relay-lite --input '{"cursor":{"first":10}}'
```

#### api assets-relay-summary
Retrieve minimal asset data — ID, name, and analytic counts only — for fast org-wide sweeps to decide which assets need deeper queries.
```bash
turbine api assets-relay-summary --input '{"cursor":{"first":10}}'
```

#### api binary-protections
List security hardening details for binaries found within the asset.
```bash
turbine api binary-protections --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api binary-protections-summary
Get aggregated counts of binary hardening features like NX or PIE.
```bash
turbine api binary-protections-summary --composed-asset-id ASSET_ID
```

#### api caas-availability
Check for the availability of the RISE AI analysis report.
```bash
turbine api caas-availability --asset-id ASSET_ID
```

#### api certificate-external-filters
Retrieve available filter options for certificate queries.
```bash
turbine api certificate-external-filters --asset-id ASSET_ID
```

#### api certificates
List X.509 certificates and validity status found in the asset.
```bash
turbine api certificates --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api credentials
Identify user accounts and password hashes discovered within the filesystem.
```bash
turbine api credentials --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api dependencies
List all software components and libraries identified in the asset.
```bash
turbine api dependencies --composed-asset-id ASSET_ID
```

#### api dependencies-lite
List dependencies with trimmed fields — keeps identity, version, license, purls, and analytic rollups; drops file metadata, digests, and nested correlation details.
```bash
turbine api dependencies-lite --composed-asset-id ASSET_ID
```

#### api dependency-known-exploits
Check if specific dependencies are linked to known public exploits.
```bash
turbine api dependency-known-exploits --input '{"identification_ids":["VALUE"],"composed_asset_id":"ASSET_ID"}'
```

#### api detailed-vulnerabilities
Retrieve in-depth vulnerability data including descriptions and CVSS vector strings.
```bash
turbine api detailed-vulnerabilities --asset-id ASSET_ID
```

#### api detailed-vulnerabilities-lite
Retrieve vulnerability descriptions with preferred CVSS v3.1 scores only — drops full v2/v4 impact blocks, exploit timelines, references, and problem type details.
```bash
turbine api detailed-vulnerabilities-lite --asset-id ASSET_ID
```

#### api download-extracted-firmware
Generate a URL to download the full unpacked file system.
```bash
turbine api download-extracted-firmware --asset-id ASSET_ID
```

#### api download-file
Create a secure link to download a specific individual file.
```bash
turbine api download-file --input '{"asset_id":"ASSET_ID","file_paths":["./path/to/file"]}'
```

#### api download-file-list
Generate a URL to download a list of all files.
```bash
turbine api download-file-list --asset-id ASSET_ID
```

#### api download-firmware
Generate a link to download the original uploaded firmware image.
```bash
turbine api download-firmware --asset-id ASSET_ID
```

#### api get-ai-model-data
Retrieve configuration and metadata for a specific AI model integration.
```bash
turbine api get-ai-model-data --composed-asset-id ASSET_ID --component-id VALUE
```

#### api get-asset-comparison-report
Retrieve a completed asset comparison report including vulnerability, component, and summary diffs.
```bash
turbine api get-asset-comparison-report --report-id VALUE
```

#### api get-certificate-reachability
Determine whether discovered certificates are reachable via executable scripts or system paths.
```bash
turbine api get-certificate-reachability --composed-asset-id ASSET_ID --file-path ./path/to/file --sha256 VALUE
```

#### api get-dependency-reachability
Determine whether a dependency is reachable via executable scripts or system paths.
```bash
turbine api get-dependency-reachability --composed-asset-id ASSET_ID --component-id VALUE
```

#### api get-secret-reachability
Determine whether discovered secrets are reachable via executable scripts or system paths.
```bash
turbine api get-secret-reachability --composed-asset-id ASSET_ID --secret-id VALUE
```

#### api get-vuln-reachability
Determine if a vulnerability can be executed via system paths.
```bash
turbine api get-vuln-reachability --input '{"asset_id":"ASSET_ID","advisory_id":"CVE_ID","identification_ids":["VALUE"]}'
```

#### api grouped-dependencies
View dependencies aggregated by vendor, license, or specific component type.
```bash
turbine api grouped-dependencies --composed-asset-id ASSET_ID --grouped-by VENDOR
```

#### api hashes
List cryptographic hashes for files identified within the asset filesystem.
```bash
turbine api hashes --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api identified-components-preview
Return organization-wide component counts filtered by enabled identification methods, with before/after deltas when verification settings change.
```bash
turbine api identified-components-preview
```

#### api license
Retrieve detailed information for a specific software license.
```bash
turbine api license --spdx-id VALUE --asset-id ASSET_ID
```

#### api license-issue
Get details about a specific license compliance issue.
```bash
turbine api license-issue --asset-id ASSET_ID --issue-id VALUE
```

#### api license-issues
List license compliance issues identified across asset components.
```bash
turbine api license-issues --asset-id ASSET_ID
```

#### api license-issues-external-filters
Retrieve available filter options for license issue queries.
```bash
turbine api license-issues-external-filters --asset-id ASSET_ID
```

#### api licenses-spdx-ids
List available SPDX license identifiers for filtering and reference.
```bash
turbine api licenses-spdx-ids
```

#### api list-ai-providers
List available AI provider integrations and their current status.
```bash
turbine api list-ai-providers
```

#### api list-asset-comparison-reports
List all asset comparison reports with pagination, filtering, and sorting.
```bash
turbine api list-asset-comparison-reports --input '{"cursor":{"first":10}}'
```

#### api list-asset-correlations
Retrieve cross-asset correlation data linking shared components and vulnerabilities.
```bash
turbine api list-asset-correlations --identifier VALUE --correlation-type UNSPECIFIED
```

#### api list-asset-crypto-libraries
List cryptographic libraries and algorithms detected within an asset.
```bash
turbine api list-asset-crypto-libraries --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api list-notification-configurations
List all notification configurations with their channels, scopes, and triggers.
```bash
turbine api list-notification-configurations --input '{"cursor":{"first":10}}'
```

#### api list-notification-logs
Retrieve a paginated log of notification delivery events and their statuses.
```bash
turbine api list-notification-logs --input '{"cursor":{"first":10}}'
```

#### api match-vulnerabilities
Find specific vulnerabilities matching a provided component identifier or package.
```bash
turbine api match-vulnerabilities --identifier VALUE
```

#### api metrics
View organization-wide statistics on asset counts, processing, and risk.
```bash
turbine api metrics
```

#### api misconfigurations
List failed security checks and configuration risks found in assets.
```bash
turbine api misconfigurations --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api misconfigurations-lite
List misconfigurations with trimmed fields — keeps check ID, name, severity, result, and correlation count; drops nested correlation objects.
```bash
turbine api misconfigurations-lite --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api org-level-information
Retrieve organization-level metadata such as last-updated time, optionally scoped by asset groups.
```bash
turbine api org-level-information
```

#### api org-level-settings
Check how the tenant organization is configured.
```bash
turbine api org-level-settings
```

#### api package-dependencies-by-id
View the dependency tree hierarchy for a specific software package.
```bash
turbine api package-dependencies-by-id --composed-asset-id ASSET_ID
```

#### api private-key-external-filters
Retrieve available filter options for private key queries.
```bash
turbine api private-key-external-filters --asset-id ASSET_ID
```

#### api private-keys
Detect private cryptographic keys stored insecurely on the asset filesystem.
```bash
turbine api private-keys --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api public-key-external-filters
Retrieve available filter options for public key queries.
```bash
turbine api public-key-external-filters --asset-id ASSET_ID
```

#### api public-keys
List public cryptographic keys found within the asset's file system.
```bash
turbine api public-keys --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api rise-ai-analysis-data
Check for the contents of the RISE AI analysis report.
```bash
turbine api rise-ai-analysis-data --asset-id ASSET_ID
```

#### api rise-ai-availability
Check eligibility and status of RISE AI analysis for an asset.
```bash
turbine api rise-ai-availability --asset-id ASSET_ID
```

#### api secret
Retrieve detailed information about a specific discovered secret.
```bash
turbine api secret --id SECRET_ID
```

#### api secret-categories-summary
Get aggregated counts of secrets grouped by category type.
```bash
turbine api secret-categories-summary --asset-id ASSET_ID
```

#### api secret-status-count
Retrieve counts of secrets grouped by remediation status.
```bash
turbine api secret-status-count --asset-id ASSET_ID
```

#### api secret-types-and-count
List secret types discovered with their occurrence counts.
```bash
turbine api secret-types-and-count --asset-id ASSET_ID
```

#### api secrets
List all secrets and sensitive data discovered within an asset.
```bash
turbine api secrets --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api secrets-summary
Get a high-level overview of secret findings and exposure metrics.
```bash
turbine api secrets-summary --asset-id ASSET_ID
```

#### api sift
Perform fuzzy hash matching to find similar code or files.
```bash
turbine api sift
```

#### api user-orgs
List all organizations the current user is authorized to access.
```bash
turbine api user-orgs
```

#### api users
Retrieve a detailed list of all users and their assigned roles.
```bash
turbine api users --input '{"cursor":{"first":10}}'
```

#### api vulnerabilities
List CVEs and associated risks for components in an asset.
```bash
turbine api vulnerabilities --asset-id ASSET_ID
```

#### api vulnerabilities-lite
List vulnerabilities with trimmed fields — keeps CVE, severity, CVSS/EPSS scores, fix versions, and correlation count; drops nested correlations and remediation details.
```bash
turbine api vulnerabilities-lite --asset-id ASSET_ID
```

#### api vulnerabilities-overview
Get a summary of vulnerability counts and severity across assets.
```bash
turbine api vulnerabilities-overview --input '{"cursor":{"first":10}}'
```

#### api vulnerability-external-filters
Count vulnerabilities matching external threat feeds like CISA or botnets.
```bash
turbine api vulnerability-external-filters --asset-id ASSET_ID
```

#### api add-asset-groups-to-assets
Associate a list of existing asset groups with selected assets.
```bash
turbine api add-asset-groups-to-assets --input '{"asset_ids":["ASSET_ID"]}'
```

#### api asset-add-dependency
Manually inject a missing dependency component into an asset's inventory.
```bash
turbine api asset-add-dependency --input '{"composed_asset_id":"ASSET_ID","dependency_fields":{"name":"my-example","type":"UNSPECIFIED"}}'
```

#### api asset-modify-dependency
Update metadata or details for a manually added asset dependency.
```bash
turbine api asset-modify-dependency --input '{"identification":{"composed_asset_id":"ASSET_ID","identification_ids":["VALUE"]},"dependency_fields":{"name":"my-example","type":"UNSPECIFIED"}}'
```

#### api asset-remove-dependencies
Remove specific dependencies from the component list of an asset.
```bash
turbine api asset-remove-dependencies --input '{"composed_asset_id":"ASSET_ID","identification_ids":["VALUE"]}'
```

#### api create-asset-comparison-report
Create a new comparison report to diff vulnerabilities and components between two assets.
```bash
turbine api create-asset-comparison-report --asset-a VALUE --asset-b VALUE
```

#### api create-notification-configuration
Create a notification configuration defining channel, scopes, and triggers for alerts.
```bash
turbine api create-notification-configuration --input '{"configuration":{"type":"NOTIFICATION_TYPE_UNSPECIFIED","channel":"NOTIFICATION_CHANNEL_UNSPECIFIED","activity_scopes":[{}]}}'
```

#### api delete-asset-comparison-report
Permanently delete an asset comparison report by its ID.
```bash
turbine api delete-asset-comparison-report --report-id VALUE --dry-run
```

#### api delete-notification-configuration
Permanently delete a notification configuration by its ID.
```bash
turbine api delete-notification-configuration --id CONFIG_ID --dry-run
```

#### api notify-notification-configuration
Send a test notification using an existing notification configuration.
```bash
turbine api notify-notification-configuration --id CONFIG_ID
```

#### api remediate-certificates
Update remediation status and notes for certificate issues found in assets.
```bash
turbine api remediate-certificates --input '{"asset_id":"ASSET_ID","certificates":[{"file_path":"./path/to/file","sha_256":"VALUE"}],"status":"UNSPECIFIED"}' --dry-run
```

#### api remediate-license-issues
Update status and add notes to resolve identified license issues.
```bash
turbine api remediate-license-issues --input '{"asset_id":"ASSET_ID","issue_ids":["VALUE"],"status":"RESOLVED"}' --dry-run
```

#### api remediate-private-keys
Apply remediation status to private key exposures discovered in assets.
```bash
turbine api remediate-private-keys --input '{"asset_id":"ASSET_ID","private_keys":[{"file_path":"./path/to/file","match_hash":"VALUE"}],"status":"UNSPECIFIED"}' --dry-run
```

#### api remediate-public-keys
Update remediation status for public key issues identified in assets.
```bash
turbine api remediate-public-keys --input '{"asset_id":"ASSET_ID","public_keys":[{"file_path":"./path/to/file","match_hash":"VALUE"}],"status":"UNSPECIFIED"}' --dry-run
```

#### api remediate-secrets
Apply remediation status and justification to exposed secrets in assets.
```bash
turbine api remediate-secrets --input '{"asset_id":"ASSET_ID","secret_ids":["VALUE"],"status":"UNSPECIFIED"}' --dry-run
```

#### api remove-all-asset-groups-from-assets
Disassociate all asset groups from a specified list of assets.
```bash
turbine api remove-all-asset-groups-from-assets --input '{"asset_ids":["ASSET_ID"]}' --dry-run
```

#### api set-asset-groups-to-asset
Replace all current group associations for an asset with new ones.
```bash
turbine api set-asset-groups-to-asset --asset-id ASSET_ID
```

#### api set-assets-to-asset-group
Overwrite the member list of an asset group with new assets.
```bash
turbine api set-assets-to-asset-group --group-id GROUP_ID
```

#### api submit-rise-ai-analysis
Request a RISE AI analysis for an eligible asset to generate insights.
```bash
turbine api submit-rise-ai-analysis --asset-id ASSET_ID
```

#### api update-notification-configuration
Update channel, scopes, triggers, or status for an existing notification configuration.
```bash
turbine api update-notification-configuration --input '{"configuration":{"id":"CONFIG_ID","name":"my-example","disabled":true,"silenced":true,"type":"NOTIFICATION_TYPE_UNSPECIFIED","channel":"NOTIFICATION_CHANNEL_UNSPECIFIED","activity_scopes":[{}],"channel_configuration":{}}}'
```

#### api update-org-level-settings
Configure global organization settings such as idle session timeout duration.
```bash
turbine api update-org-level-settings --idle-timout-enabled
```

#### api user-action
Perform administrative actions like enabling or disabling specific user accounts.
```bash
turbine api user-action --type DISABLE --user-id USER_ID
```

#### api user-reset-password
Trigger a password reset email for a specific user account.
```bash
turbine api user-reset-password --id USER_ID
```

#### api user-set-user-role
Assign a new permission role like Owner or Operator to users.
```bash
turbine api user-set-user-role --next-role VALUE --user-id USER_ID
```

#### api user-update-user
Modify user profile information including name and contact email details.
```bash
turbine api user-update-user --user-id USER_ID
```

<!-- AUTO-GENERATED-HUMAN-EXAMPLES:END -->
