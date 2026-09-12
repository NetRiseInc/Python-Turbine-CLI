# Turbine CLI — Human guide

Resource-oriented commands for everyday Turbine work. Use `turbine api` when you need the full GraphQL surface.

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
List activity-log events for an asset.
```bash
turbine asset activity ASSET_ID
```

#### asset files
List every file extracted from an asset.
```bash
turbine asset files ASSET_ID
```

#### asset get
Show one asset by ID.
```bash
turbine asset get ASSET_ID
```

#### asset hashes
List file hashes for an asset.
```bash
turbine asset hashes ASSET_ID
```

#### asset list --detail full
List assets with the full nested payload.
```bash
turbine asset list --detail full --limit 20
```

#### asset list --detail lite
List assets with identity, status, and risk (default).
```bash
turbine asset list --detail lite --limit 20 --fields id,name,status
```

#### asset list --detail overview
List assets with overview risk rollups.
```bash
turbine asset list --detail overview --limit 20
```

#### asset list --detail summary
List assets as id, name, and analytic counts only.
```bash
turbine asset list --detail summary --limit 20
```

#### asset risk
Summarize every finding category for one asset.
```bash
turbine asset risk ASSET_ID
```

#### asset status
Check whether an asset is still processing.
```bash
turbine asset status ASSET_ID
```

#### asset submit
Submit metadata for an upload already in progress.
```bash
turbine asset submit --name my-example
```

#### asset update
Update an asset's name or other metadata.
```bash
turbine asset update --id ASSET_ID
```

#### asset upload
Upload a firmware or SBOM file for analysis.
```bash
turbine asset upload firmware.bin --name my-firmware
```

#### asset upload-dir
Upload every file in a directory as assets.
```bash
turbine asset upload-dir ./firmware-dir
```

#### auth login
Verify credentials and save non-secrets to the config file.
```bash
turbine auth login --save
```

#### auth status
Show whether the current credentials can reach the API.
```bash
turbine auth status
```

#### cert list
List X.509 certificates found in an asset.
```bash
turbine cert list ASSET_ID --limit 50
```

#### component crypto
List crypto libraries detected in an asset.
```bash
turbine component crypto ASSET_ID
```

#### component grouped
List dependencies grouped by vendor, license, or type.
```bash
turbine component grouped ASSET_ID
```

#### component list --detail full
List components with the full nested payload.
```bash
turbine component list ASSET_ID --detail full
```

#### component list --detail lite
List components with identity, version, and license.
```bash
turbine component list ASSET_ID --detail lite
```

#### credential list
List accounts and password hashes found in an asset.
```bash
turbine credential list ASSET_ID
```

#### group add-assets
Add assets to an asset group.
```bash
turbine group add-assets --id GROUP_ID --input '{"assetIds":["ASSET_ID"]}'
```

#### group create
Create a named asset group.
```bash
turbine group create --name my-group --description 'Example group'
```

#### group delete
Delete an asset group (assets stay in the org).
```bash
turbine group delete GROUP_ID
```

#### group list
List asset groups.
```bash
turbine group list --limit 20
```

#### group members
List assets in an asset group.
```bash
turbine group members GROUP_ID
```

#### group remove-assets
Remove assets from an asset group.
```bash
turbine group remove-assets --id GROUP_ID --input '{"assetIds":["ASSET_ID"]}'
```

#### group update
Rename an asset group.
```bash
turbine group update --id GROUP_ID --name renamed-group
```

#### key list --type private
List private keys found in an asset.
```bash
turbine key list ASSET_ID --type private
```

#### key list --type public
List public keys found in an asset.
```bash
turbine key list ASSET_ID --type public
```

#### license list
List license compliance issues on an asset.
```bash
turbine license list ASSET_ID
```

#### misconfig list --detail full
List misconfigurations with full correlation objects.
```bash
turbine misconfig list ASSET_ID --detail full
```

#### misconfig list --detail lite
List misconfigurations with check ID and severity.
```bash
turbine misconfig list ASSET_ID --detail lite
```

#### notification list
List notification configurations.
```bash
turbine notification list
```

#### org info
Show organization metadata.
```bash
turbine org info
```

#### org settings
Show organization settings.
```bash
turbine org settings
```

#### protection list
List binary hardening details for an asset.
```bash
turbine protection list ASSET_ID
```

#### report list
List asset comparison reports.
```bash
turbine report list
```

#### search
Keyword-search artifacts and files across the org.
```bash
turbine search search_term
```

#### secret list
List secrets discovered in an asset.
```bash
turbine secret list ASSET_ID --limit 50
```

#### user delete
Delete a user account (dry-run first).
```bash
turbine user delete USER_ID --dry-run
```

#### user invite
Invite a user to the organization.
```bash
turbine user invite --email user@example.com --role MEMBER
```

#### user list
List users in the organization.
```bash
turbine user list --limit 20
```

#### user remove
Remove a user from the org without deleting the account.
```bash
turbine user remove USER_ID --dry-run
```

#### vuln get
Show one vulnerability by ID.
```bash
turbine vuln get CVE_ID
```

#### vuln get --detail lite
Show one vulnerability with preferred CVSS v3.1 only.
```bash
turbine vuln get CVE_ID --detail lite
```

#### vuln list --detail detailed
List vulns with descriptions and full CVSS vectors.
```bash
turbine vuln list ASSET_ID --detail detailed
```

#### vuln list --detail detailed-lite
List vulns with description and preferred CVSS v3.1.
```bash
turbine vuln list ASSET_ID --detail detailed-lite
```

#### vuln list --detail full
List vulns with correlations and remediation details.
```bash
turbine vuln list ASSET_ID --detail full
```

#### vuln list --detail lite
List vulns with CVE, severity, and scores (default).
```bash
turbine vuln list ASSET_ID --detail lite --limit 50
```

#### vuln overview
List vulnerability counts across assets.
```bash
turbine vuln overview --limit 20
```

#### vuln remediate
Set VEX status for one asset vulnerability.
```bash
turbine vuln remediate --asset ASSET_ID --input '{"remediationId":{"vulnerabilityId":"CVE_ID"},"status":"NOT_AFFECTED","justification":"CODE_NOT_PRESENT"}' --dry-run
```

#### vuln remediate --all
Apply VEX status to every vuln matching a filter.
```bash
turbine vuln remediate --asset ASSET_ID --all --input '{"vulnerabilityFilter":{},"status":"NOT_AFFECTED","justification":"CODE_NOT_PRESENT"}' --dry-run
```

#### vuln remediate --bulk
Bulk-apply VEX status to selected asset vulns.
```bash
turbine vuln remediate --asset ASSET_ID --bulk --input '{"remediationIds":[{"vulnerabilityId":"CVE_ID"}],"status":"NOT_AFFECTED","justification":"CODE_NOT_PRESENT"}' --dry-run
```

## API operations

#### api activity
List activity-log events for an asset.
```bash
turbine api activity --asset-id ASSET_ID
```

#### api analytics
Get org dashboard risk metrics and chart data.
```bash
turbine api analytics
```

#### api asset-group-analytics
Get risk metrics for one asset group.
```bash
turbine api asset-group-analytics --group-id GROUP_ID
```

#### api asset-group-members
List assets in an asset group.
```bash
turbine api asset-group-members --input '{"group_id":"GROUP_ID","cursor":{"first":10}}'
```

#### api asset-groups
List asset groups with pagination and filters.
```bash
turbine api asset-groups --input '{"cursor":{"first":10}}'
```

#### api asset-upload
Get a pre-signed URL to upload a file for analysis.
```bash
turbine api asset-upload --upload-id UPLOAD_ID
```

#### api asset-vulnerability-remediation
Get VEX status and justification for one vuln on an asset.
```bash
turbine api asset-vulnerability-remediation --asset-id ASSET_ID --remediation-id VALUE --vulnerability-id CVE_ID
```

#### api assets-overview
Get risk and threat rollups across assets.
```bash
turbine api assets-overview --input '{"cursor":{"first":10}}'
```

#### api assets-relay
List assets with full nested fields (paginated).
```bash
turbine api assets-relay --input '{"cursor":{"first":10}}'
```

#### api assets-relay-lite
List assets with identity, status, risk, and analytic rollups.
```bash
turbine api assets-relay-lite --input '{"cursor":{"first":10}}'
```

#### api assets-relay-summary
List assets as id, name, and analytic counts only.
```bash
turbine api assets-relay-summary --input '{"cursor":{"first":10}}'
```

#### api binary-protections
List binary hardening details for an asset.
```bash
turbine api binary-protections --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api binary-protections-summary
Get counts of hardening features such as NX or PIE.
```bash
turbine api binary-protections-summary --composed-asset-id ASSET_ID
```

#### api caas-availability
Check whether a RiseAI analysis report is available.
```bash
turbine api caas-availability --asset-id ASSET_ID
```

#### api certificate-external-filters
List filter options for certificate queries.
```bash
turbine api certificate-external-filters --asset-id ASSET_ID
```

#### api certificates
List X.509 certificates found in an asset.
```bash
turbine api certificates --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api credentials
List accounts and password hashes found in an asset.
```bash
turbine api credentials --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api dependencies
List software components identified in an asset.
```bash
turbine api dependencies --composed-asset-id ASSET_ID
```

#### api dependencies-lite
List components with identity, version, license, and rollups.
```bash
turbine api dependencies-lite --composed-asset-id ASSET_ID
```

#### api dependency-known-exploits
Check whether dependencies link to known public exploits.
```bash
turbine api dependency-known-exploits --input '{"identification_ids":["VALUE"],"composed_asset_id":"ASSET_ID"}'
```

#### api detailed-vulnerabilities
List vulns with descriptions and full CVSS vectors.
```bash
turbine api detailed-vulnerabilities --asset-id ASSET_ID
```

#### api detailed-vulnerabilities-lite
List vulns with description and preferred CVSS v3.1 only.
```bash
turbine api detailed-vulnerabilities-lite --asset-id ASSET_ID
```

#### api download-extracted-firmware
Get a URL to download the unpacked filesystem.
```bash
turbine api download-extracted-firmware --asset-id ASSET_ID
```

#### api download-file
Get a URL to download one extracted file.
```bash
turbine api download-file --input '{"asset_id":"ASSET_ID","file_paths":["./path/to/file"]}'
```

#### api download-file-list
Get a URL to download the asset file listing.
```bash
turbine api download-file-list --asset-id ASSET_ID
```

#### api download-firmware
Get a URL to download the original uploaded image.
```bash
turbine api download-firmware --asset-id ASSET_ID
```

#### api get-ai-model-data
Get config and metadata for an AI model integration.
```bash
turbine api get-ai-model-data --composed-asset-id ASSET_ID --component-id VALUE
```

#### api get-asset-comparison-report
Get a finished asset comparison report.
```bash
turbine api get-asset-comparison-report --report-id VALUE
```

#### api get-certificate-reachability
Check whether certificates are reachable via paths or scripts.
```bash
turbine api get-certificate-reachability --composed-asset-id ASSET_ID --file-path ./path/to/file --sha256 VALUE
```

#### api get-dependency-reachability
Check whether a dependency is reachable via paths or scripts.
```bash
turbine api get-dependency-reachability --composed-asset-id ASSET_ID --component-id VALUE
```

#### api get-my-permissions
List permission IDs held by the calling user.
```bash
turbine api get-my-permissions
```

#### api get-resource-permissions
List the caller's effective permissions on a resource.
```bash
turbine api get-resource-permissions
```

#### api get-role
Get one RBAC role by ID.
```bash
turbine api get-role
```

#### api get-role-delete-impact
Preview who loses access if a custom role is deleted.
```bash
turbine api get-role-delete-impact
```

#### api get-secret-reachability
Check whether secrets are reachable via paths or scripts.
```bash
turbine api get-secret-reachability --composed-asset-id ASSET_ID --secret-id VALUE
```

#### api get-security-group-delete-impact
Preview who loses access if a security group is deleted.
```bash
turbine api get-security-group-delete-impact
```

#### api get-vuln-reachability
Check whether a vulnerability is reachable via system paths.
```bash
turbine api get-vuln-reachability --input '{"asset_id":"ASSET_ID","advisory_id":"CVE_ID","identification_ids":["VALUE"]}'
```

#### api grouped-dependencies
List dependencies grouped by vendor, license, or type.
```bash
turbine api grouped-dependencies --composed-asset-id ASSET_ID --grouped-by VENDOR
```

#### api hashes
List file hashes from an asset filesystem.
```bash
turbine api hashes --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api identified-components-preview
Preview org-wide component counts under identification settings.
```bash
turbine api identified-components-preview
```

#### api jira-integration
Get Jira integration summary and connection health.
```bash
turbine api jira-integration
```

#### api jira-integration-setup
Get the current Jira setup-wizard state.
```bash
turbine api jira-integration-setup
```

#### api jira-project-components
List Jira project components for a connected space.
```bash
turbine api jira-project-components --space-id VALUE
```

#### api jira-project-labels
Search Jira labels for a connected space.
```bash
turbine api jira-project-labels --space-id VALUE --query search_term
```

#### api jira-project-sprints
Search Jira sprints for a connected space.
```bash
turbine api jira-project-sprints --space-id VALUE --query search_term
```

#### api jira-project-teams
Search Atlassian Teams for a connected Jira space.
```bash
turbine api jira-project-teams --space-id VALUE --query search_term
```

#### api jira-project-users
Search assignable Jira users for a connected space.
```bash
turbine api jira-project-users --space-id VALUE --query search_term
```

#### api jira-project-versions
List Jira project versions for a connected space.
```bash
turbine api jira-project-versions --space-id VALUE
```

#### api jira-space-issue-fields
List creatable fields for a Jira space and issue type.
```bash
turbine api jira-space-issue-fields --space-id VALUE --issue-type-id VALUE
```

#### api jira-space-issue-types
List issue types for a connected Jira space.
```bash
turbine api jira-space-issue-types --space-id VALUE
```

#### api jira-space-workflow-config
Get status mappings and workflow config for a Jira space.
```bash
turbine api jira-space-workflow-config --space-id VALUE --issue-type-id VALUE
```

#### api jira-status-mapping-problems
List status-mapping problems across connected Jira spaces.
```bash
turbine api jira-status-mapping-problems
```

#### api license
Get details for one software license.
```bash
turbine api license --spdx-id VALUE --asset-id ASSET_ID
```

#### api license-issue
Get details for one license compliance issue.
```bash
turbine api license-issue --asset-id ASSET_ID --issue-id VALUE
```

#### api license-issues
List license compliance issues on an asset.
```bash
turbine api license-issues --asset-id ASSET_ID
```

#### api license-issues-external-filters
List filter options for license-issue queries.
```bash
turbine api license-issues-external-filters --asset-id ASSET_ID
```

#### api licenses-spdx-ids
List SPDX license identifiers.
```bash
turbine api licenses-spdx-ids
```

#### api list-ac-rs
List access control records, optionally for one user.
```bash
turbine api list-ac-rs
```

#### api list-ai-providers
List AI provider integrations and their status.
```bash
turbine api list-ai-providers
```

#### api list-asset-comparison-reports
List asset comparison reports with filters and sorting.
```bash
turbine api list-asset-comparison-reports --input '{"cursor":{"first":10}}'
```

#### api list-asset-correlations
List cross-asset correlations for shared components or vulns.
```bash
turbine api list-asset-correlations --identifier VALUE --correlation-type UNSPECIFIED
```

#### api list-asset-crypto-libraries
List crypto libraries detected in an asset.
```bash
turbine api list-asset-crypto-libraries --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api list-entity-assets
List assets a user or security group can access.
```bash
turbine api list-entity-assets
```

#### api list-my-ac-rs
List access control records that apply to you.
```bash
turbine api list-my-ac-rs
```

#### api list-my-security-groups
List security groups you belong to.
```bash
turbine api list-my-security-groups
```

#### api list-notification-configurations
List notification configurations and their triggers.
```bash
turbine api list-notification-configurations --input '{"cursor":{"first":10}}'
```

#### api list-notification-logs
List notification delivery events and statuses.
```bash
turbine api list-notification-logs --input '{"cursor":{"first":10}}'
```

#### api list-org-users
List org users with groups and accessible asset counts.
```bash
turbine api list-org-users
```

#### api list-permissions
List the permission catalog for custom roles.
```bash
turbine api list-permissions
```

#### api list-roles
List RBAC roles for the current organization.
```bash
turbine api list-roles
```

#### api list-security-group-members
List members of a security group.
```bash
turbine api list-security-group-members
```

#### api list-security-groups
List RBAC security groups for the current org.
```bash
turbine api list-security-groups
```

#### api match-vulnerabilities
Find vulnerabilities matching a component or package.
```bash
turbine api match-vulnerabilities --identifier VALUE
```

#### api me
Get the authenticated user's profile.
```bash
turbine api me
```

#### api metrics
Get org-wide counts for assets, processing, and risk.
```bash
turbine api metrics
```

#### api misconfigurations
List failed security checks on an asset.
```bash
turbine api misconfigurations --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api misconfigurations-lite
List misconfigs with check ID, severity, result, and counts.
```bash
turbine api misconfigurations-lite --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api org-level-information
Get org metadata such as last-updated time.
```bash
turbine api org-level-information
```

#### api org-level-settings
Get the tenant organization's settings.
```bash
turbine api org-level-settings
```

#### api package-dependencies-by-id
Get the dependency tree for one package.
```bash
turbine api package-dependencies-by-id --composed-asset-id ASSET_ID
```

#### api private-key-external-filters
List filter options for private-key queries.
```bash
turbine api private-key-external-filters --asset-id ASSET_ID
```

#### api private-keys
List private keys found in an asset filesystem.
```bash
turbine api private-keys --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api public-key-external-filters
List filter options for public-key queries.
```bash
turbine api public-key-external-filters --asset-id ASSET_ID
```

#### api public-keys
List public keys found in an asset filesystem.
```bash
turbine api public-keys --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api remediated-vulnerabilities-by-asset
List remediated vulns for one status bucket, by asset.
```bash
turbine api remediated-vulnerabilities-by-asset --input '{"cursor":{"first":10},"status":"UNSPECIFIED"}'
```

#### api rise-ai-analysis-data
Get the contents of a RiseAI analysis report.
```bash
turbine api rise-ai-analysis-data --asset-id ASSET_ID
```

#### api rise-ai-availability
Check RiseAI eligibility and status for an asset.
```bash
turbine api rise-ai-availability --asset-id ASSET_ID
```

#### api secret
Get details for one discovered secret.
```bash
turbine api secret --id SECRET_ID
```

#### api secret-categories-summary
Get secret counts grouped by category.
```bash
turbine api secret-categories-summary --asset-id ASSET_ID
```

#### api secret-status-count
Get secret counts grouped by remediation status.
```bash
turbine api secret-status-count --asset-id ASSET_ID
```

#### api secret-types-and-count
List secret types with occurrence counts.
```bash
turbine api secret-types-and-count --asset-id ASSET_ID
```

#### api secrets
List secrets discovered in an asset.
```bash
turbine api secrets --input '{"asset_id":"ASSET_ID","cursor":{"first":10}}'
```

#### api secrets-summary
Get a summary of secret findings on an asset.
```bash
turbine api secrets-summary --asset-id ASSET_ID
```

#### api sift
Fuzzy-hash match to find similar code or files.
```bash
turbine api sift
```

#### api user-orgs
List organizations the current user can access.
```bash
turbine api user-orgs
```

#### api users
List users and their assigned roles.
```bash
turbine api users --input '{"cursor":{"first":10}}'
```

#### api vulnerabilities
List CVEs on an asset with scores and fix versions.
```bash
turbine api vulnerabilities --asset-id ASSET_ID
```

#### api vulnerabilities-lite
List vulns with CVE, severity, scores, and counts.
```bash
turbine api vulnerabilities-lite --asset-id ASSET_ID
```

#### api vulnerabilities-overview
Get vulnerability counts and severity across assets.
```bash
turbine api vulnerabilities-overview --input '{"cursor":{"first":10}}'
```

#### api vulnerability-external-filters
Count vulns matching threat feeds such as CISA KEV.
```bash
turbine api vulnerability-external-filters --asset-id ASSET_ID
```

#### api vulnerability-jira-tickets
List Jira tickets linked to a vuln on an asset.
```bash
turbine api vulnerability-jira-tickets --asset-id ASSET_ID --advisory-id CVE_ID --component-id VALUE
```

#### api vulnerability-remediation-summary
Get org-wide counts of applied VEX statuses.
```bash
turbine api vulnerability-remediation-summary
```

#### api add-asset-groups-to-assets
Attach asset groups to one or more assets.
```bash
turbine api add-asset-groups-to-assets --input '{"asset_ids":["ASSET_ID"]}'
```

#### api add-security-group-member
Add a user to an RBAC security group.
```bash
turbine api add-security-group-member --security-group-id GROUP_ID --user-id USER_ID
```

#### api asset-add-dependency
Add a manual dependency component to an asset.
```bash
turbine api asset-add-dependency --input '{"composed_asset_id":"ASSET_ID","dependency_fields":{"name":"my-example","type":"UNSPECIFIED"}}'
```

#### api asset-modify-dependency
Update a manually added asset dependency.
```bash
turbine api asset-modify-dependency --input '{"identification":{"composed_asset_id":"ASSET_ID","identification_ids":["VALUE"]},"dependency_fields":{"name":"my-example","type":"UNSPECIFIED"}}'
```

#### api asset-remove-dependencies
Remove selected dependencies from an asset.
```bash
turbine api asset-remove-dependencies --input '{"composed_asset_id":"ASSET_ID","identification_ids":["VALUE"]}'
```

#### api bulk-delete-ac-rs
Delete many access control records; missing ones count as success.
```bash
turbine api bulk-delete-ac-rs --input '{"acr_ids":["VALUE"]}'
```

#### api create-acr
Grant a user or security group a role on a resource.
```bash
turbine api create-acr --input '{"binding":{"entity_type":"USER","entity_id":"VALUE","resource_type":"ORGANIZATION"}}'
```

#### api create-asset-comparison-report
Start a comparison report between two assets.
```bash
turbine api create-asset-comparison-report --asset-a VALUE --asset-b VALUE
```

#### api create-custom-role
Create an org-scoped custom role with chosen permissions.
```bash
turbine api create-custom-role --input '{"name":"my-example","permissions":["VALUE"]}'
```

#### api create-notification-configuration
Create a notification channel, scopes, and triggers.
```bash
turbine api create-notification-configuration --input '{"configuration":{"type":"NOTIFICATION_TYPE_UNSPECIFIED","channel":"NOTIFICATION_CHANNEL_UNSPECIFIED","activity_scopes":[{}]}}'
```

#### api create-security-group
Create an RBAC security group in the current org.
```bash
turbine api create-security-group --name my-example
```

#### api delete-acr
Delete one access control record.
```bash
turbine api delete-acr --acr-id VALUE --dry-run
```

#### api delete-asset-comparison-report
Delete an asset comparison report by ID.
```bash
turbine api delete-asset-comparison-report --report-id VALUE --dry-run
```

#### api delete-custom-role
Delete a custom role from the organization.
```bash
turbine api delete-custom-role --role-id VALUE --dry-run
```

#### api delete-notification-configuration
Delete a notification configuration by ID.
```bash
turbine api delete-notification-configuration --id CONFIG_ID --dry-run
```

#### api delete-security-group
Delete a security group from the organization.
```bash
turbine api delete-security-group --security-group-id GROUP_ID --dry-run
```

#### api invite-user
Invite a user with a role and optional security groups.
```bash
turbine api invite-user --email user@example.com
```

#### api jira-integration-add-connected-space
Connect a Jira space to the integration.
```bash
turbine api jira-integration-add-connected-space
```

#### api jira-integration-create-issue
Create a Jira issue, optionally linked to a finding.
```bash
turbine api jira-integration-create-issue --space-id VALUE --issue-type-id VALUE --summary VALUE --description VALUE
```

#### api jira-integration-delete-connected-space
Disconnect a Jira space from the integration.
```bash
turbine api jira-integration-delete-connected-space --space-id VALUE
```

#### api jira-integration-disconnect
Disconnect the Jira integration from the org.
```bash
turbine api jira-integration-disconnect
```

#### api jira-integration-reconnect
Re-enable Jira when OAuth and app install are already done.
```bash
turbine api jira-integration-reconnect
```

#### api jira-integration-set-status-mapping-auto-sync
Enable or disable auto-sync for Jira status mappings.
```bash
turbine api jira-integration-set-status-mapping-auto-sync --enabled
```

#### api jira-integration-setup-action
Run a step in the Jira setup or reconnect flow.
```bash
turbine api jira-integration-setup-action --action START
```

#### api jira-integration-test-connection
Check that the Jira integration connection is healthy.
```bash
turbine api jira-integration-test-connection
```

#### api notify-notification-configuration
Send a test notification for a configuration.
```bash
turbine api notify-notification-configuration --id CONFIG_ID
```

#### api remediate-certificates
Set remediation status and notes on certificate findings.
```bash
turbine api remediate-certificates --input '{"asset_id":"ASSET_ID","certificates":[{"file_path":"./path/to/file","sha_256":"VALUE"}],"status":"UNSPECIFIED"}' --dry-run
```

#### api remediate-license-issues
Set status and notes on license compliance issues.
```bash
turbine api remediate-license-issues --input '{"asset_id":"ASSET_ID","issue_ids":["VALUE"],"status":"RESOLVED"}' --dry-run
```

#### api remediate-private-keys
Set remediation status on private key findings.
```bash
turbine api remediate-private-keys --input '{"asset_id":"ASSET_ID","private_keys":[{"file_path":"./path/to/file","match_hash":"VALUE"}],"status":"UNSPECIFIED"}' --dry-run
```

#### api remediate-public-keys
Set remediation status on public key findings.
```bash
turbine api remediate-public-keys --input '{"asset_id":"ASSET_ID","public_keys":[{"file_path":"./path/to/file","match_hash":"VALUE"}],"status":"UNSPECIFIED"}' --dry-run
```

#### api remediate-secrets
Set remediation status and justification on secrets.
```bash
turbine api remediate-secrets --input '{"asset_id":"ASSET_ID","secret_ids":["VALUE"],"status":"UNSPECIFIED"}' --dry-run
```

#### api remove-all-asset-groups-from-assets
Detach every asset group from the given assets.
```bash
turbine api remove-all-asset-groups-from-assets --input '{"asset_ids":["ASSET_ID"]}' --dry-run
```

#### api remove-org-user
Remove a user from the current organization.
```bash
turbine api remove-org-user --user-id USER_ID --dry-run
```

#### api remove-security-group-member
Remove a user from an RBAC security group.
```bash
turbine api remove-security-group-member --security-group-id GROUP_ID --user-id USER_ID --dry-run
```

#### api replace-acr
Replace an access control record in one delete-and-create.
```bash
turbine api replace-acr --input '{"acr_id":"VALUE","binding":{"entity_type":"USER","entity_id":"VALUE","resource_type":"ORGANIZATION"}}'
```

#### api save-jira-space-workflow-config
Save status mappings and workflow config for a Jira space.
```bash
turbine api save-jira-space-workflow-config --input '{"space_id":"VALUE","issue_type_id":"VALUE","mappings":[{"jira_status_id":"VALUE"}],"resolution_status_ids":["VALUE"]}'
```

#### api set-asset-groups-to-asset
Replace an asset's group memberships.
```bash
turbine api set-asset-groups-to-asset --asset-id ASSET_ID
```

#### api set-assets-to-asset-group
Replace an asset group's member list.
```bash
turbine api set-assets-to-asset-group --group-id GROUP_ID
```

#### api set-org-user-status
Enable or disable a user in the current org.
```bash
turbine api set-org-user-status --user-id USER_ID --status ENABLED
```

#### api submit-rise-ai-analysis
Request a RiseAI analysis for an eligible asset.
```bash
turbine api submit-rise-ai-analysis --asset-id ASSET_ID
```

#### api update-custom-role
Update a custom role's name, description, or permissions.
```bash
turbine api update-custom-role --input '{"role_id":"VALUE","name":"my-example","permissions":["VALUE"]}'
```

#### api update-notification-configuration
Update a notification configuration's channel or triggers.
```bash
turbine api update-notification-configuration --input '{"configuration":{"id":"CONFIG_ID","name":"my-example","disabled":true,"silenced":true,"type":"NOTIFICATION_TYPE_UNSPECIFIED","channel":"NOTIFICATION_CHANNEL_UNSPECIFIED","activity_scopes":[{}],"channel_configuration":{}}}'
```

#### api update-org-level-settings
Update org settings such as idle session timeout.
```bash
turbine api update-org-level-settings --idle-timout-enabled
```

#### api update-security-group
Update a security group's name or description.
```bash
turbine api update-security-group --security-group-id GROUP_ID --name my-example
```

#### api user-action
Enable or disable a user account.
```bash
turbine api user-action --type DISABLE --user-id USER_ID
```

#### api user-reset-password
Send a password-reset email to a user.
```bash
turbine api user-reset-password --id USER_ID
```

#### api user-set-user-role
Assign a role such as Owner or Operator.
```bash
turbine api user-set-user-role --next-role VALUE --user-id USER_ID
```

#### api user-update-user
Update a user's name or email.
```bash
turbine api user-update-user --user-id USER_ID
```

<!-- AUTO-GENERATED-HUMAN-EXAMPLES:END -->
