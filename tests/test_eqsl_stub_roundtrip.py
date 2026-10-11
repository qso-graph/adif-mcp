"""End-to-end-ish tests for the eQSL stub tools: fetch + summarize."""

from __future__ import annotations

from typing import Any, cast

from adif_mcp.tools.eqsl_stub import fetch_inbox, filter_summary


def test_fetch_inbox_shape_and_counts() -> None:
    """Fetch returns {records:[...]}; summarize matches total size."""
    out = fetch_inbox("KI7MT")
    records = out["records"]
    assert isinstance(records, list) and len(records) > 0

    sb = filter_summary(records, by="band")["summary"]
    sm = filter_summary(records, by="mode")["summary"]

    assert sum(sb.values()) == len(records)
    assert sum(sm.values()) == len(records)


def test_filter_summary_by_invalid_key() -> None:
    """Unknown summary selector should raise a ValueError."""
    out = fetch_inbox("KI7MT")
    records = out["records"]
    try:
        # Pass an invalid selector, bypassing the static Literal type:
        filter_summary(records, by=cast(Any, "continent"))["summary"]
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for invalid 'by' selector")


def test_filter_summary_by_valid_keys() -> None:
    """Verify other valid keys (call, qso_date) work."""
    out = fetch_inbox("KI7MT")
    records = out["records"]

    sc = filter_summary(records, by="call")["summary"]
    sd = filter_summary(records, by="qso_date")["summary"]

    assert sum(sc.values()) == len(records)
    assert sum(sd.values()) == len(records)
