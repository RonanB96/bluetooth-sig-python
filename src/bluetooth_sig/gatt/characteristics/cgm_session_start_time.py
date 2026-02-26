"""CGM Session Start Time characteristic implementation.

Implements the CGM Session Start Time characteristic (0x2AAA).

Structure (from GSS YAML):
    Session Start Time (7 bytes) -- DateTime struct (year+month+day+h+m+s)
    Time Zone (1 byte, uint8) -- offset from UTC in 15-minute increments
    DST Offset (1 byte, uint8) -- DST adjustment code
    E2E-CRC (2 bytes, uint16, optional)

References:
    Bluetooth SIG Continuous Glucose Monitoring Service
    org.bluetooth.characteristic.cgm_session_start_time (GSS YAML)
"""

from __future__ import annotations

from datetime import datetime

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .dst_offset import DSTOffset
from .utils import DataParser


class CGMSessionStartTimeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from CGM Session Start Time characteristic.

    Attributes:
        start_time: Session start date and time.
        time_zone: Time zone offset from UTC in 15-minute increments.
        dst_offset: DST adjustment code.
        e2e_crc: E2E-CRC value. None if absent.

    """

    start_time: datetime
    time_zone: int
    dst_offset: DSTOffset
    e2e_crc: int | None = None


class CGMSessionStartTimeCharacteristic(BaseCharacteristic[CGMSessionStartTimeData]):
    """CGM Session Start Time characteristic (0x2AAA).

    Reports the session start time, time zone, and DST offset
    for a CGM session.
    """

    expected_type = CGMSessionStartTimeData
    min_length: int = 9  # datetime(7) + timezone(1) + dst(1)
    allow_variable_length: bool = True  # optional E2E-CRC

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> CGMSessionStartTimeData:
        """Parse CGM Session Start Time from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic (9 or 11 bytes).
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            CGMSessionStartTimeData with parsed date/time and timezone info.

        """
        year = DataParser.parse_int16(data, 0, signed=False)
        month = data[2]
        day = data[3]
        hour = data[4]
        minute = data[5]
        second = data[6]
        start_time = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)

        time_zone = data[7]
        dst_offset = DSTOffset(data[8])

        _min_length_with_crc = 11
        e2e_crc: int | None = None
        if len(data) >= _min_length_with_crc:
            e2e_crc = DataParser.parse_int16(data, 9, signed=False)

        return CGMSessionStartTimeData(
            start_time=start_time,
            time_zone=time_zone,
            dst_offset=dst_offset,
            e2e_crc=e2e_crc,
        )

    def _encode_value(self, data: CGMSessionStartTimeData) -> bytearray:
        """Encode CGMSessionStartTimeData back to BLE bytes.

        Args:
            data: CGMSessionStartTimeData instance.

        Returns:
            Encoded bytearray (9 or 11 bytes).

        """
        result = bytearray()
        result.extend(DataParser.encode_int16(data.start_time.year, signed=False))
        result.append(data.start_time.month)
        result.append(data.start_time.day)
        result.append(data.start_time.hour)
        result.append(data.start_time.minute)
        result.append(data.start_time.second)
        result.append(data.time_zone)
        result.append(int(data.dst_offset))

        if data.e2e_crc is not None:
            result.extend(DataParser.encode_int16(data.e2e_crc, signed=False))

        return result
