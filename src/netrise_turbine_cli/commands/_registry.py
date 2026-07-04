"""Registry mapping detail levels and resources to SDK iterator methods."""

from __future__ import annotations

ASSET_LIST_METHODS = {
    "overview": "iter_assets_overview",
    "summary": "iter_assets_relay_summary",
    "lite": "iter_assets_relay_lite",
    "full": "iter_assets_relay",
}

VULN_LIST_METHODS = {
    "full": "iter_vulnerabilities",
    "lite": "iter_vulnerabilities_lite",
    "detailed": "iter_detailed_vulnerabilities",
    "detailed-lite": "iter_detailed_vulnerabilities_lite",
}

COMPONENT_LIST_METHODS = {
    "full": "iter_dependencies",
    "lite": "iter_dependencies_lite",
}

MISCONFIG_LIST_METHODS = {
    "full": "iter_misconfigurations",
    "lite": "iter_misconfigurations_lite",
}

KEY_LIST_METHODS = {
    "private": "iter_private_keys",
    "public": "iter_public_keys",
}
