#!/usr/bin/env python3
"""
Hatch build hook: writes ADIF metadata from pyproject.toml into the package.

During `uv build` / `hatchling` builds, this hook reads:

  [tool.adif]
  spec_version = "3.1.7"
  features = ["core QSO model", "band/mode/QSL_RCVD enums"]

…and emits `src/adif_mcp/adif_meta.json` so the wheel/sdist contains a
machine-readable copy of the ADIF compatibility information.
"""

from __future__ import annotations

import json
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

# ---- Typed base for static checkers; real base only at build time ----
if TYPE_CHECKING:

    class _Base:
        """Typed stand-in for Hatch's BuildHookInterface (type checking only)."""

        PLUGIN_NAME: str

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Initialize the hook (stub only, no runtime logic)."""

        def initialize(self, version: str, build_data: dict[str, Any]) -> None:
            """Stub initializer; overridden by the real Hatch interface at runtime."""

else:
    # Imported only when the build backend runs (hatchling present then).
    from hatchling.builders.hooks.plugin.interface import BuildHookInterface as _Base


def _load_adif_meta(pyproject_path: Path) -> dict[str, Any]:
    """Load ADIF metadata from *pyproject_path*.

    Returns:
        A dict with keys:
          - "spec_version": str
          - "features": list[str]
    """
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    tool = data.get("tool", {})
    adif = tool.get("adif", {})
    spec = adif.get("spec_version", "unknown")
    features = adif.get("features", [])
    return {"spec_version": spec, "features": features}


def _write_meta_json(path: Path, payload: dict[str, Any]) -> None:
    """Write *payload* as pretty JSON to *path*, creating parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class BuildHook(_Base):
    """Hatch build hook that generates `adif_mcp/adif_meta.json`."""

    PLUGIN_NAME = "adif-meta"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Create `adif_meta.json` before wheel/sdist are built."""
        pyproject = Path("pyproject.toml")
        payload = _load_adif_meta(pyproject)
        payload["build_flavor"] = version  # e.g., "standard"
        _write_meta_json(Path("src/adif_mcp/adif_meta.json"), payload)
