# tests/test_manifest_shape.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

import pytest

try:
    # Preferred: package validator
    from adif_mcp.tools.validate_manifest import validate_one as _validate_one

    validate_one: Callable[[Path], int] = _validate_one
except Exception:
    # Typed fallback with a minimal shape check so the test still has value.
    def _fallback_validate_one(p: Path) -> int:
        data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
        tools = data.get("tools", None)
        if not isinstance(tools, list) or not tools:
            raise AssertionError("manifest missing non-empty 'tools' list")
        return 0

    validate_one = _fallback_validate_one


def _pkg_manifest_path() -> Path | None:
    """
    Return the packaged manifest if available, else None.
    We avoid importlib.resources in tests to keep it simple across envs.
    """
    p = Path("src/adif_mcp/mcp/manifest.json")
    return p if p.exists() else None


def _repo_manifest_path() -> Path | None:
    """Return a repo-root manifest (legacy/dev) if present, else None."""
    p = Path("mcp/manifest.json")
    return p if p.exists() else None


def _load_manifest_any() -> Tuple[Path, Dict[str, Any]]:
    """
    Load the first manifest we can find (packaged preferred, repo fallback).
    Skip the test if none exists.
    """
    p = _pkg_manifest_path() or _repo_manifest_path()
    if not p:
        pytest.skip("No manifest.json found in package or repo.")
    data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return p, data


def test_validate_manifest_via_validator_or_fallback() -> None:
    """
    Use the shipped validator when available, otherwise a typed fallback.
    """
    p, _ = _load_manifest_any()
    assert validate_one(p) == 0


def test_manifest_has_non_empty_tools_array() -> None:
    """The manifest must include a non-empty 'tools' list."""
    p, data = _load_manifest_any()
    assert "tools" in data, f"manifest.tools missing in {p}"
    tools = data["tools"]
    assert isinstance(tools, list) and tools, "manifest.tools must be a non-empty list"


def test_examples_json_round_trip() -> None:
    """If present, each tool's examples must be JSON-serializable objects."""
    _, data = _load_manifest_any()
    tools = data.get("tools", [])
    for tool in tools:
        examples = tool.get("examples", [])
        assert isinstance(examples, list)
        for ex in examples:
            assert isinstance(ex, dict)
            # Round-trip sanity
            assert isinstance(json.loads(json.dumps(ex)), dict)
