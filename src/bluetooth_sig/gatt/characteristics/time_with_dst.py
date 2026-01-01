"""Time with DST characteristic (0x2A11) implementation.

Represents the date and time of the next Daylight Saving Time change.
Used by Next DST Change Service (0x1807).

Based on Bluetooth SIG GATT Specification:
- Time with DST: 10 bytes (same structure as Current Time)
- Date Time: Year (uint16) + Month + Day + Hours + Minutes + Seconds (7 bytes)
- Day of Week: uint8 (1=Monday to 7=Sunday, 0=Unknown)
- Fractions256: uint8 (0-255, representing 1/256 fractions of a second)
- Adjust Reason: uint8 bitfield (Manual Update, External Reference, Time Zone, DST)
"""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import TimeDataTemplate


class TimeWithDstCharacteristic(BaseCharacteristic):
    """Time with DST characteristic (0x2A11).

    Represents the date and time when the next Daylight Saving Time change occurs.

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

    def __init__(self) -> None:
        """Initialize the Time with DST characteristic."""
        super().__init__()
        self._template = TimeDataTemplate()
