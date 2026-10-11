"""Pydantic models (QSO, enums) validation and normalization."""

from __future__ import annotations

from datetime import date, time
from typing import Any, Dict

from adif_mcp.models import QSO


def test_valid_qso_parses() -> None:
    """A normal record validates cleanly."""
    raw: Dict[str, Any] = {
        "station_call": "KI7MT",
        "call": "K7ABC",
        "qso_date": date(2025, 1, 1),
        "time_on": time(12, 0),
        "band": "20m",
        "mode": "ft8",
    }
    rec = QSO(**raw)
    assert rec.band == "20M"
    assert rec.mode == "FT8"
