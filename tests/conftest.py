# tests/conftest.py
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def load_env_defaults(p: Path) -> Dict[str, object]:
    """Load a JSON file of environment defaults as a dict[str, object]."""
    data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return dict(data)


def _load_sample(name: str) -> Dict[str, object]:
    """Load a test JSON blob from tests/data and return as dict[str, object]."""
    here = Path(__file__).parent / "data"
    data: Dict[str, Any] = json.loads((here / name).read_text(encoding="utf-8"))
    return dict(data)


def records_min() -> List[Dict[str, str]]:
    """Return one minimal QSO record as a list of dict[str, str]."""
    return [
        {
            "station_call": "KI7MT",
            "call": "K7ABC",
            "qso_date": "20250101",
            "time_on": "010203",
            "band": "20m",
            "mode": "FT8",
            "rst_sent": "59",
            "rst_rcvd": "59",
            "freq": "14.074",
            "gridsquare": "DN41",
        }
    ]


def records_two_modes() -> List[Dict[str, str]]:
    """Return two records with different modes for summary tests."""
    return [
        {
            "station_call": "KI7MT",
            "call": "K7ABC",
            "qso_date": "20250101",
            "time_on": "010203",
            "band": "20m",
            "mode": "FT8",
            "rst_sent": "59",
            "rst_rcvd": "59",
            "freq": "14.074",
            "gridsquare": "DN41",
        },
        {
            "station_call": "KI7MT",
            "call": "K7XYZ",
            "qso_date": "20250102",
            "time_on": "020304",
            "band": "20m",
            "mode": "CW",
            "rst_sent": "599",
            "rst_rcvd": "599",
            "freq": "14.020",
            "gridsquare": "DN41",
        },
    ]


# ---------------------------
# Pytest fixtures
# ---------------------------


