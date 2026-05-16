# src/adif_mcp/__init__.py
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Final

# Resolve once, then bind to Final exactly once
try:
    _pkg_version = version("adif-mcp")
except PackageNotFoundError:  # local dev / editable installs without dist metadata
    _pkg_version = "0.0.0"

__version__: Final[str] = _pkg_version
__adif_spec__: Final[str] = "3.1.7"
