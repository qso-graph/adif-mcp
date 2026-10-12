"""Test resource loading for spec and mapping JSON files."""

from adif_mcp.resources import (
    get_adif_catalog,
    get_adif_meta,
)


def test_adif_meta_has_version() -> None:
    """adif_meta.json loads and names its spec version."""
    meta = get_adif_meta()
    assert "spec_version" in meta


def test_adif_catalog_fields_nonempty() -> None:
    """adif_catalog.json loads with a non-empty field list."""
    cat = get_adif_catalog()
    assert isinstance(cat.get("fields"), list) and cat["fields"]

