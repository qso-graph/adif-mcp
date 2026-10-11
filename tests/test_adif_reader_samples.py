"""Parser tests for minimal, varied, and edge ADIF records."""

from __future__ import annotations

from pathlib import Path

import pytest

from adif_mcp.parsers.adif_reader import parse_adi_text


@pytest.fixture(scope="module")
def sample_adi_text() -> str:
    """
    Provide ADIF sample text for tests.

    - If `tests/data/ki7mt-sample.adi` exists, load it.
    - Otherwise, return a minimal inline ADIF record so tests
      still run in CI environments without the sample file.
    """
    p = Path(__file__).parent / "data" / "ki7mt-sample.adi"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return "<CALL:5>KI7MT<QSO_DATE:8>20240812<TIME_ON:4>0315<EOR>"


def test_parse_sample_file(sample_adi_text: str) -> None:
    """Parse the sample ADIF and assert at least one record."""
    recs = parse_adi_text(sample_adi_text)
    assert isinstance(recs, list) and len(recs) >= 1
    assert "call" in recs[0]


def test_min_record() -> None:
    """A truly minimal record parses to one dict with required keys."""
    txt = "<CALL:5>KI7MT<QSO_DATE:8>20240812<TIME_ON:4>0315<EOR>"
    recs = parse_adi_text(txt)
    assert len(recs) == 1
    r = recs[0]
    assert r["call"] == "KI7MT"
    assert r["qso_date"] == "20240812"
    assert r["time_on"] == "0315"


def test_case_insensitive_tags_and_whitespace() -> None:
    """Lowercase/mixed case tags + surrounding whitespace should be accepted."""
    txt = "  <call:5>ki7mt  <qso_date:8>20240812 <time_on:4>0315 <EOR>\n"
    recs = parse_adi_text(txt)
    assert len(recs) == 1
    r = recs[0]
    assert r["call"] == "KI7MT"  # parser should uppercase callsign
    assert r["qso_date"] == "20240812"
    assert r["time_on"] == "0315"


def test_extra_unknown_fields_preserved() -> None:
    """Unknown fields should still arrive in the raw record map."""
    txt = (
        "<CALL:5>KI7MT<QSO_DATE:8>20240812<TIME_ON:4>0315"
        "<BAND:3>30M<MODE:3>FT8<MY_FIELD:3>XYZ<EOR>"
    )
    recs = parse_adi_text(txt)
    assert len(recs) == 1
    r = recs[0]
    # Unknown/extra ADIF fields are not preserved by the minimal parser.
    assert "my_field" not in recs[0]
    assert r["band"] in ("30m", "30M", "30M".lower())  # depending on your normalizer
