"""Exact Time 256 characteristic implementation."""

from __future__ import annotations

from datetime import datetime

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ExactTime256Data(msgspec.Struct, frozen=True, kw_only=True):
    """Exact time with 1/256 second resolution.

    Attributes:
        dt: Python datetime for date and time components
        day_of_week: Day of week (1=Monday, 7=Sunday, 0=Unknown)
        fractions256: Fractions of a second (1/256 resolution, 0-255)
    """

    dt: datetime
    day_of_week: int
    fractions256: int


class ExactTime256Characteristic(BaseCharacteristic[ExactTime256Data]):
    """Exact Time 256 characteristic (0x2A0C).

    org.bluetooth.characteristic.exact_time_256

    Represents exact time with 1/256 second resolution in 9-byte format.
    """

    expected_length = 9

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ExactTime256Data:
        """Parse exact time 256 value.

        Args:
            data: Raw bytearray from BLE characteristic (9 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True)

        Returns:
            ExactTime256Data with datetime, day_of_week, and fractions256.
        """
        dt = datetime(
            year=DataParser.parse_int16(data, 0, signed=False),
            month=data[2],
            day=data[3],
            hour=data[4],
            minute=data[5],
            second=data[6],
        )
        return ExactTime256Data(dt=dt, day_of_week=data[7], fractions256=data[8])

    def _encode_value(self, data: ExactTime256Data) -> bytearray:
        """Encode exact time 256 value back to bytes.

        Args:
            data: ExactTime256Data to encode

        Returns:
            Encoded bytes (9 bytes)
        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.dt.year, signed=False))
        result.append(data.dt.month)
        result.append(data.dt.day)
        result.append(data.dt.hour)
        result.append(data.dt.minute)
        result.append(data.dt.second)
        result.append(data.day_of_week)
        result.append(data.fractions256)
        return result
