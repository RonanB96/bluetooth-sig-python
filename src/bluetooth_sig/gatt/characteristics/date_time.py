"""Date Time characteristic implementation."""

from __future__ import annotations

from datetime import datetime

from ...types.gatt_enums import ValueType
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class DateTimeCharacteristic(BaseCharacteristic[datetime]):
    """Date Time characteristic (0x2A08).

    org.bluetooth.characteristic.date_time

    Represents date and time in 7-byte format: year(2), month(1), day(1), hours(1), minutes(1), seconds(1).
    """

    _manual_value_type = ValueType.DATETIME
    expected_length = 7

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> datetime:
        """Parse date time value.

        Args:
            data: Raw bytearray from BLE characteristic (7 bytes, validated by base class).
            ctx: Optional CharacteristicContext.

        Returns:
            Python datetime object with parsed date and time.
        """
        return datetime(
            year=DataParser.parse_int16(data, 0, signed=False),
            month=data[2],
            day=data[3],
            hour=data[4],
            minute=data[5],
            second=data[6],
        )

    def _encode_value(self, data: datetime) -> bytearray:
        """Encode datetime value back to bytes.

        Args:
            data: Python datetime object to encode

        Returns:
            Encoded bytes (7 bytes)
        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.year, signed=False))
        result.append(data.month)
        result.append(data.day)
        result.append(data.hour)
        result.append(data.minute)
        result.append(data.second)
        return result
