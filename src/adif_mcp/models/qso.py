"""ADIF 3.1.7 QSO Model definition."""

from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class QSO(BaseModel):
    """
    Represents a single ADIF 3.1.7 QSO record.

    Strictly typed to prevent hallucinations and ensure protocol integrity.
    """

    call: str = Field(..., min_length=3, description="Callsign of the contacted station")
    qso_date: date = Field(..., description="Date of the QSO (UTC)")
    time_on: time = Field(..., description="Time the QSO started (UTC)")
    band: str = Field(..., description="Amateur radio band (e.g., 20m, 40m)")
    mode: str = Field(..., description="Transmission mode (e.g., CW, SSB, FT8)")

    # Optional fields commonly used
    rst_sent: Optional[str] = Field(None, description="Signal report sent")
    rst_rcvd: Optional[str] = Field(None, description="Signal report received")
    name: Optional[str] = Field(None, description="Name of the contacted operator")
    comment: Optional[str] = Field(None, description="Comment field")

    @field_validator("call", "band", "mode")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Ensure ADIF fields that require uppercase are normalized."""
        return v.upper()
