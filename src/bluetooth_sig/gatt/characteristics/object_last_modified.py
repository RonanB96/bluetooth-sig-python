"""Object Last-Modified characteristic implementation."""

from __future__ import annotations

from datetime import datetime

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ObjectLastModifiedCharacteristic(BaseCharacteristic[datetime]):
    """Object Last-Modified characteristic (0x2AC2).

    org.bluetooth.characteristic.object_last_modified

    Represents the date/time when an OTS object was last modified.
    Uses the standard Date Time format: year (uint16), month (uint8),
    day (uint8), hours (uint8), minutes (uint8), seconds (uint8).
    """

    expected_length: int = 7
    min_length: int = 7

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> datetime:
        """Parse object last-modified date/time.

        Args:
            data: Raw bytes (7 bytes, Date Time format).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Python datetime object.

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
        """Encode datetime to Date Time format bytes.

        Args:
            data: Python datetime object.

        Returns:
            Encoded bytes (7 bytes).

        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.year, signed=False))
        result.append(data.month)
        result.append(data.day)
        result.append(data.hour)
        result.append(data.minute)
        result.append(data.second)
        return result
