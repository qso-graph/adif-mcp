"""adif-mcp resources

Provides access to:
- adif_meta.json (spec metadata)
- adif_catalog.json (field catalog)
"""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any, cast

# -------- Spec --------


def get_adif_meta() -> dict[str, Any]:
    """Load ADIF specification metadata."""
    p = files("adif_mcp.resources.spec").joinpath("adif_meta.json")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))


def get_adif_catalog() -> dict[str, Any]:
    """Load ADIF field catalog."""
    p = files("adif_mcp.resources.spec").joinpath("adif_catalog.json")
    return cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))

