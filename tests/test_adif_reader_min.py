# /uss/bin//env python3

"""Test parsing of the smallest valid ADIF record.

This ensures that `parse_adi_text` correctly handles a minimal QSO entry
containing only the required fields (CALL, QSO_DATE, TIME_ON).

Verifies:
    - Exactly one record is returned.
    - The parsed values for CALL, QSO_DATE, and TIME_ON match the input.
"""

from adif_mcp.parsers.adif_reader import parse_adi_text


def test_min_record() -> None:
    """Parse a singel record for testing"""
    txt = "<CALL:5>KI7MT<QSO_DATE:8>20240812<TIME_ON:4>0315<EOR>"
    recs = parse_adi_text(txt)
    assert len(recs) == 1
    r = recs[0]
    assert r["call"] == "KI7MT"
    assert r["qso_date"] == "20240812"
    assert r["time_on"] == "0315"
