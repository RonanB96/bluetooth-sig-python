"""Current Time characteristic (0x2A2B) implementation.

Represents exact time with date, time, fractions, and adjustment reasons.
Used by Current Time Service (0x1805).

Based on Bluetooth SIG GATT Specification:
- Current Time: 10 bytes (Date Time + Day of Week + Fractions256 + Adjust Reason)
- Date Time: Year (uint16) + Month + Day + Hours + Minutes + Seconds (7 bytes)
- Day of Week: uint8 (1=Monday to 7=Sunday, 0=Unknown)
- Fractions256: uint8 (0-255, representing 1/256 fractions of a second)
- Adjust Reason: uint8 bitfield (Manual Update, External Reference, Time Zone, DST)
"""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import TimeDataTemplate


class CurrentTimeCharacteristic(BaseCharacteristic):
    """Current Time characteristic (0x2A2B).

    Represents exact time with date, time, fractions, and adjustment reasons.
    Used by Current Time Service (0x1805).

    Structure (10 bytes):
    - Year: uint16 (1582-9999, 0=unknown)
    - Month: uint8 (1-12, 0=unknown)
    - Day: uint8 (1-31, 0=unknown)
    - Hours: uint8 (0-23)
    - Minutes: uint8 (0-59)
    - Seconds: uint8 (0-59)
    - Day of Week: uint8 (0=unknown, 1=Monday...7=Sunday)
    - Fractions256: uint8 (0-255, representing 1/256 fractions of a second)
    - Adjust Reason: uint8 bitfield
    """

    # Validation attributes
    _manual_value_type: ValueType | str | None = ValueType.DICT

    def __init__(self) -> None:
        """Initialize the Current Time characteristic."""
        super().__init__()
        self._template = TimeDataTemplate()
