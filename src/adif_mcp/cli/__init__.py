"""
CLI package initializer for adif-mcp.

Exposes the root entrypoint (`main`) so that subcommands can be discovered
and invoked. This module should remain minimal — primarily wiring and
namespace setup.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Final

from .root import main

# Resolve once, then bind to Final exactly once
try:
    _pkg_version = version("adif-mcp")
except PackageNotFoundError:  # local dev / editable installs without dist metadata
    _pkg_version = "0.0.0"

__version__: Final[str] = _pkg_version
__adif_spec__: Final[str] = "3.1.7"

__all__: list[str] = []

if __name__ == "__main__":
    main()
