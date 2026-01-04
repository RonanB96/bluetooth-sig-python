"""Day Date Time characteristic implementation."""

from __future__ import annotations

from datetime import datetime

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class DayDateTimeData(msgspec.Struct, frozen=True, kw_only=True):
    """Day, date and time data structure with day of week.

    Attributes:
        dt: Python datetime for date and time components
        day_of_week: Day of week (1=Monday, 7=Sunday, 0=Unknown)
    """

    dt: datetime
    day_of_week: int


class DayDateTimeCharacteristic(BaseCharacteristic[DayDateTimeData]):
    """Day Date Time characteristic (0x2A0A).

    org.bluetooth.characteristic.day_date_time

    Represents date, time and day of week in 8-byte format.
    """

    _manual_value_type = "DayDateTimeData"
    expected_length = 8

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> DayDateTimeData:
        """Parse day date time value.

        Args:
            data: Raw bytearray from BLE characteristic (8 bytes).
            ctx: Optional CharacteristicContext.

        Returns:
            DayDateTimeData with datetime and day_of_week.
        """
        dt = datetime(
            year=DataParser.parse_int16(data, 0, signed=False),
            month=data[2],
            day=data[3],
            hour=data[4],
            minute=data[5],
            second=data[6],
        )
        return DayDateTimeData(dt=dt, day_of_week=data[7])

    def _encode_value(self, data: DayDateTimeData) -> bytearray:
        """Encode day date time value back to bytes.

        Args:
            data: DayDateTimeData to encode

        Returns:
            Encoded bytes (8 bytes)
        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.dt.year, signed=False))
        result.append(data.dt.month)
        result.append(data.dt.day)
        result.append(data.dt.hour)
        result.append(data.dt.minute)
        result.append(data.dt.second)
        result.append(data.day_of_week)
        return result
