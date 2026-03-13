"""Test resource loading for spec and mapping JSON files."""

from adif_mcp.resources import (
    get_adif_catalog,
    get_adif_meta,
    get_usage_map,
)


def test_adif_meta_has_version() -> None:
    meta = get_adif_meta()
    assert "spec_version" in meta


def test_adif_catalog_fields_nonempty() -> None:
    cat = get_adif_catalog()
    assert isinstance(cat.get("fields"), list) and cat["fields"]


def test_usage_map_loads() -> None:
    usage = get_usage_map()
    assert isinstance(usage, dict) and len(usage) > 0
