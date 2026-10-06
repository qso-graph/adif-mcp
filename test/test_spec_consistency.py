"""Consistency of the packaged ADIF spec files (issue #8).

Each spec directory holds ADIF's own exports (all.json, enumerations.json and one
enumerations_<name>.json per enumeration) plus enumerations adif-mcp derives
itself (Country). These tests keep the two apart:

- the combined files and the per-file exports must describe exactly the same
  enumerations, record for record, so a bulk loader reading either gets the same data;
- every per-file enumeration must be either an ADIF export or declared derived,
  so a file of ours can never pass as ADIF's;
- the derived Country table must still match the DXCC entity names it comes from.
"""

import glob
import json
import os
from typing import Any, Dict

import pytest

from adif_mcp.mcp.server import DERIVED_ENUMERATIONS, ENUMERATION_FIELDS

_SPEC = os.path.join(os.path.dirname(__file__), "..", "src", "adif_mcp", "resources", "spec")
VERSIONS = {"316": "3.1.6", "317": "3.1.7"}


def _load(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)["Adif"]
    return data


def _per_file(version_dir: str) -> Dict[str, Dict[str, Any]]:
    """Map enumeration name -> the 'Adif' block of its per-file JSON."""
    out: Dict[str, Dict[str, Any]] = {}
    for path in glob.glob(os.path.join(_SPEC, version_dir, "enumerations_*.json")):
        adif = _load(path)
        (name,) = adif["Enumerations"].keys()
        out[name] = adif
    return out


@pytest.mark.parametrize("version_dir,version", VERSIONS.items())
def test_combined_files_equal_upstream_per_file_set(version_dir: str, version: str) -> None:
    """all.json, enumerations.json and the ADIF per-file exports agree exactly."""
    upstream = {
        name: adif["Enumerations"][name]
        for name, adif in _per_file(version_dir).items()
        if name not in DERIVED_ENUMERATIONS
    }
    for combined in ("all.json", "enumerations.json"):
        enums = _load(os.path.join(_SPEC, version_dir, combined))["Enumerations"]
        assert set(enums) == set(upstream), combined
        for name, enum in upstream.items():
            assert enums[name] == enum, f"{combined}: {name} differs"


@pytest.mark.parametrize("version_dir,version", VERSIONS.items())
def test_every_enumeration_is_adif_or_declared_derived(version_dir: str, version: str) -> None:
    """ADIF exports carry ADIF's version header; derived files carry a Derived block."""
    for name, adif in _per_file(version_dir).items():
        if name in DERIVED_ENUMERATIONS:
            assert "Derived" in adif, f"{name} is derived but not labelled"
            assert "Version" not in adif, f"{name} is derived but claims an ADIF version"
        else:
            assert adif.get("Version") == version, f"{name} is not an ADIF {version} export"
            assert "Derived" not in adif, name


@pytest.mark.parametrize("version_dir", VERSIONS)
def test_server_lists_exactly_the_packaged_enumerations(version_dir: str) -> None:
    """The server's enumeration table matches the files, derived set included."""
    assert set(ENUMERATION_FIELDS) == set(_per_file(version_dir))
    assert set(DERIVED_ENUMERATIONS) <= set(ENUMERATION_FIELDS)


@pytest.mark.parametrize("version_dir", VERSIONS)
def test_country_matches_dxcc_entity_names(version_dir: str) -> None:
    """Country is DXCC_Entity_Code's Entity Name column, deleted entities Import-only."""
    dxcc = _per_file(version_dir)["DXCC_Entity_Code"]["Enumerations"]["DXCC_Entity_Code"]
    country = _per_file(version_dir)["Country"]["Enumerations"]["Country"]["Records"]
    expected = {
        rec["Entity Name"]: (rec["Entity Code"], rec.get("Deleted") == "true")
        for rec in dxcc["Records"].values()
        if rec["Entity Code"] != "0"
    }
    actual = {
        name: (rec["DXCC Entity Code"], rec.get("Import-only") == "true")
        for name, rec in country.items()
    }
    assert actual == expected


_UPSTREAM = os.path.join(os.path.dirname(__file__), "data", "adif_upstream_sha256.json")


@pytest.mark.parametrize("version_dir", VERSIONS)
def test_upstream_files_match_adif_org_checksums(version_dir: str) -> None:
    """Every ADIF file we package, in every format, is byte-identical to adif.org.uk's
    (#8, #28), and nothing of ADIF's is missing or extra.

    The SHA-256 values come from ADIF's published resource zip, so a change here
    is our change, never mistaken for an upstream one.
    """
    import hashlib

    with open(_UPSTREAM, encoding="utf-8") as f:
        pinned = json.load(f)["versions"][version_dir]["files"]
    base = os.path.join(_SPEC, version_dir)
    packaged = {
        os.path.relpath(p, base).replace(os.sep, "/")
        for p in glob.glob(os.path.join(base, "**", "*"), recursive=True)
        if os.path.isfile(p)
    }
    assert packaged - set(pinned) == {"enumerations_country.json", "MANIFEST.json"}
    assert set(pinned) <= packaged
    for name, sha in pinned.items():
        with open(os.path.join(base, name), "rb") as fh:
            assert hashlib.sha256(fh.read()).hexdigest() == sha, name


@pytest.mark.parametrize("version_dir", VERSIONS)
def test_shipped_manifest_matches_the_pins(version_dir: str) -> None:
    """The MANIFEST.json users can check against is exactly what the tests pin (#28)."""
    with open(_UPSTREAM, encoding="utf-8") as f:
        pinned = json.load(f)["versions"][version_dir]
    with open(os.path.join(_SPEC, version_dir, "MANIFEST.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["files"] == pinned["files"]
    assert manifest["zip_sha256"] == pinned["zip_sha256"]
    assert manifest["source"] == pinned["source"]


@pytest.mark.parametrize("version_dir", VERSIONS)
def test_every_format_shipped_but_no_tests(version_dir: str) -> None:
    """ADIF's full release except its test material (#28)."""
    with open(_UPSTREAM, encoding="utf-8") as f:
        pinned = json.load(f)["versions"][version_dir]["files"]
    formats = {name.split("/")[0] for name in pinned if "/" in name}
    assert formats == {"csv", "ods", "tsv", "xlsx", "xml"}
    assert {"xml/all.xml", "xml/adifexport.xsd", "all.json"} <= set(pinned)
    assert not any(name.startswith("tests/") or "test_QSOs" in name for name in pinned)


def test_two_adif_versions_shipped() -> None:
    """The previous ADIF version and the current one; never more (KI7MT, 2026-10-06)."""
    assert len(VERSIONS) == 2
