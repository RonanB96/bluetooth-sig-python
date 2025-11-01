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

from datetime import datetime

import msgspec

from ...types.gatt_enums import DayOfWeek
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import IEEE11073Parser

# Bluetooth SIG Current Time characteristic constants
CURRENT_TIME_LENGTH = 10  # Total characteristic length in bytes
DAY_OF_WEEK_MAX = 7  # Maximum day of week value (0=unknown, 1-7=Mon-Sun)
FRACTIONS256_MAX = 255  # Maximum fractions256 value
ADJUST_REASON_MAX = 255  # Maximum adjust reason value


class CurrentTimeData(msgspec.Struct):
    """Current Time characteristic data structure."""

    date_time: datetime | None  # None if year/month/day are 0 (unknown)
    day_of_week: DayOfWeek
    fractions256: int  # 0-255 (1/256 fractions of a second)
    adjust_reason: int  # Bitfield of AdjustReason flags


class CurrentTimeCharacteristic(BaseCharacteristic):
    """Current Time characteristic (0x2A2B).

    Represents exact time with date, time, day of week, sub-second precision,
    and reasons for time adjustment.

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

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> CurrentTimeData:
        """Decode Current Time data from bytes.

        Args:
            data: Raw characteristic data (10 bytes)
            ctx: Optional characteristic context

        Returns:
            CurrentTimeData with all time fields

        Raises:
            ValueError: If data is insufficient or contains invalid values

        """
        if len(data) < CURRENT_TIME_LENGTH:
            raise ValueError(
                f"Insufficient data for Current Time: expected {CURRENT_TIME_LENGTH} bytes, got {len(data)}"
            )

        # Parse Date Time (7 bytes) - handle unknown (0) values
        year = int.from_bytes(data[0:2], "little")
        month = data[2]
        day = data[3]

        # If year, month, or day is 0 (unknown), set date_time to None
        if year == 0 or month == 0 or day == 0:
            date_time = None
        else:
            date_time = IEEE11073Parser.parse_timestamp(data, 0)

        # Parse Day of Week (1 byte)
        day_of_week_raw = data[7]
        if day_of_week_raw > DAY_OF_WEEK_MAX:
            raise ValueError(f"Invalid day of week: {day_of_week_raw} (valid range: 0-{DAY_OF_WEEK_MAX})")
        day_of_week = DayOfWeek(day_of_week_raw)

        # Parse Fractions256 (1 byte)
        fractions256 = data[8]

        # Parse Adjust Reason (1 byte)
        adjust_reason = data[9]

        return CurrentTimeData(
            date_time=date_time,
            day_of_week=day_of_week,
            fractions256=fractions256,
            adjust_reason=adjust_reason,
        )

    def encode_value(self, data: CurrentTimeData) -> bytearray:
        """Encode Current Time data to bytes.

        Args:
            data: CurrentTimeData to encode

        Returns:
            Encoded current time (10 bytes)

        Raises:
            ValueError: If data contains invalid values

        """
        result = bytearray()

        # Encode Date Time (7 bytes)
        if data.date_time is None:
            # Unknown date/time: all zeros
            result.extend(bytearray(IEEE11073Parser.TIMESTAMP_LENGTH))
        else:
            result.extend(IEEE11073Parser.encode_timestamp(data.date_time))

        # Encode Day of Week (1 byte)
        day_of_week_value = int(data.day_of_week)
        if day_of_week_value > DAY_OF_WEEK_MAX:
            raise ValueError(f"Invalid day of week: {day_of_week_value} (valid range: 0-{DAY_OF_WEEK_MAX})")
        result.append(day_of_week_value)

        # Encode Fractions256 (1 byte)
        if data.fractions256 > FRACTIONS256_MAX:
            raise ValueError(f"Invalid fractions256: {data.fractions256} (valid range: 0-{FRACTIONS256_MAX})")
        result.append(data.fractions256)

        # Encode Adjust Reason (1 byte)
        if data.adjust_reason > ADJUST_REASON_MAX:
            raise ValueError(f"Invalid adjust_reason: {data.adjust_reason} (valid range: 0-{ADJUST_REASON_MAX})")
        result.append(data.adjust_reason)

        return result
