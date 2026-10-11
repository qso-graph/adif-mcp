"""Unit tests for the ADIF-MCP server and its internal logic."""

import tempfile

import pytest

from adif_mcp.mcp.server import parse_adif
from adif_mcp.utils.geography import (
    calculate_distance_impl,
    calculate_heading_impl,
)


def test_calculate_distance() -> None:
    """
    Verify calculate_distance_impl returns a reasonable float for known grids.
    FN20 to FN21 is 1 degree latitude difference (~111 km).
    """
    # FN20 center: 40.5, -73.0
    # FN21 center: 41.5, -73.0
    dist = calculate_distance_impl("FN20", "FN21")
    assert 110.0 < dist < 112.0


def test_calculate_heading() -> None:
    """
    Verify calculate_heading_impl returns a valid azimuth.
    FN20 (NY) to IO91 (London) should be Northeast (~50-55 deg).
    """
    heading = calculate_heading_impl("FN20", "IO91")
    assert 45.0 < heading < 60.0


@pytest.mark.asyncio
async def test_parse_adif_tool() -> None:
    """
    Verify the parse_adif tool actually parses an ADIF file from disk.
    """
    adi_content = "<CALL:5>KI7MT<QSO_DATE:8>20250101<BAND:3>20m<EOR>\n"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".adi", delete=False
    ) as tmp:
        tmp.write(adi_content)
        tmp_path = tmp.name

    recs = await parse_adif(tmp_path)

    assert len(recs) == 1
    raw_output = recs[0].text

    # Verify parsed output (not error text)
    assert "TOTAL RECORDS: 1" in raw_output
    assert "RECORD 1" in raw_output
    assert "KI7MT" in raw_output
    assert "20250101" in raw_output


def test_geography_invalid_locator() -> None:
    """Verify that invalid locators raise ValueError in the utility."""
    with pytest.raises(ValueError, match="at least 4 characters"):
        calculate_distance_impl("FN2", "FN20")
