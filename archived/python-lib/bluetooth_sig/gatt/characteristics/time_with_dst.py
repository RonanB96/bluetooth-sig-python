"""Time with DST characteristic (0x2A11).

Represents the date and time with DST offset information.
Structure: DateTime(7 bytes) + DST Offset(1 byte) = 8 bytes total.

References:
    Bluetooth SIG Assigned Numbers / GATT Service Specifications
"""

from __future__ import annotations

import struct
from datetime import datetime

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .dst_offset import DSTOffset


class TimeWithDstData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed Time with DST data."""

    dt: datetime
    dst_offset: DSTOffset


class TimeWithDstCharacteristic(BaseCharacteristic[TimeWithDstData]):
    """Time with DST characteristic (0x2A11).

    Structure (8 bytes):
    - DateTime: Year(uint16) + Month(uint8) + Day(uint8) + Hours(uint8) + Minutes(uint8) + Seconds(uint8) = 7 bytes
    - DST Offset: uint8 = 1 byte
    """

    min_length: int | None = 8
    max_length: int | None = 8

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> TimeWithDstData:
        """Parse Time with DST data.

        Format: DateTime(7) + DSTOffset(1).
        """
        year, month, day, hours, minutes, seconds = struct.unpack("<HBBBBB", data[0:7])
        dt = datetime(year, month, day, hours, minutes, seconds)
        dst_offset = DSTOffset(data[7])
        return TimeWithDstData(dt=dt, dst_offset=dst_offset)

    def _encode_value(self, data: TimeWithDstData) -> bytearray:
        """Encode Time with DST value back to bytes."""
        result = bytearray(
            struct.pack(
                "<HBBBBB",
                data.dt.year,
                data.dt.month,
                data.dt.day,
                data.dt.hour,
                data.dt.minute,
                data.dt.second,
            )
        )
        result.append(int(data.dst_offset))
        return result
