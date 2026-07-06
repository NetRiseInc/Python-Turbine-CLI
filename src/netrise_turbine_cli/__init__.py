"""NetRise Turbine CLI."""

from importlib.metadata import PackageNotFoundError, version

try:
    # Single source of truth: the version in pyproject.toml, read from the
    # installed package metadata (the publish target bumps only pyproject).
    __version__ = version("netrise-turbine-cli")
except PackageNotFoundError:  # running from source without an install
    __version__ = "0.0.0+unknown"
