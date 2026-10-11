"""Test suite for the eQSL stub tools.

These tests validate that the placeholder `fetch_inbox` and `filter_summary`
functions in `adif_mcp.tools.eqsl_stub` return data in the expected shape
and that summaries match the number of generated records.

The tests are lightweight and operate on synthetic data only.
"""

from typing import Callable, List

from adif_mcp.parsers.adif_reader import QSORecord
from adif_mcp.tools.eqsl_stub import fetch_inbox, filter_summary


def test_fetch_inbox_shape() -> None:
    """Ensure fetch_inbox() returns records with expected ADIF-like fields."""
    out = fetch_inbox("KI7MT")
    assert "records" in out and isinstance(out["records"], list)
    assert all(
        {"station_call", "call", "qso_date", "time_on", "band", "mode"}.issubset(r.keys())
        for r in out["records"]
    )


def test_summary_band_mode() -> None:
    """Ensure filter_summary() aggregates counts correctly by band and mode."""
    recs: List[QSORecord] = fetch_inbox("KI7MT")["records"]
    sb = filter_summary(recs, by="band")["summary"]
    sm = filter_summary(recs, by="mode")["summary"]
    assert isinstance(sb, dict) and isinstance(sm, dict)
    assert sum(sb.values()) == len(recs)
    assert sum(sm.values()) == len(recs)


def test_inbox_factory_variants(
    inbox_for_callsign: Callable[[str], List[QSORecord]],
) -> None:
    """Factory fixture returns plausible data for different calls."""
    a = inbox_for_callsign("KI7MT")
    b = inbox_for_callsign("K7ABC")
    assert isinstance(a, list) and isinstance(b, list)
    assert a and b  # both non-empty synthetic inboxes
