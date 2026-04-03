"""Device Time characteristic (0x2B90).

Per DTS v1.0 Table 3.6, this characteristic uses epoch-based Base_Time
(uint32 seconds since 1900-01-01 or 2000-01-01 per DT_Status bit 4), NOT
the 7-byte Date-Time format used by other time characteristics.

Mandatory field layout (8 octets minimum, without E2E_CRC prefix):
  Offset  Field        Type    Octets  Unit
  0       Base_Time    uint32  4       seconds since epoch
  4       Time_Zone    sint8   1       15-minute units (-48..+56)
  5       DST_Offset   uint8   1       0=Std, 2=+0.5h, 4=+1h, 8=+2h, 255=Unknown
  6       DT_Status    uint16  2       status bitfield (Table 3.7)

Optional trailing fields (present when corresponding feature flags are set):
  User_Time (uint32), Accumulated_RTC_Drift (uint16),
  Next_Sequence_Number (uint16), Base_Time_Second_Fractions (uint16).

Total: 8-20 octets (without E2E_CRC).

References:
    Bluetooth SIG Device Time Service v1.0, Table 3.6, Table 3.7
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_MIN_LENGTH = 8


class DTStatus(IntFlag):
    """DT_Status bitfield — DTS v1.0 Table 3.7.

    Bits 7-15 are Reserved for Future Use.
    """

    TIME_FAULT = 0x0001  # Bit 0
    UTC_ALIGNED = 0x0002  # Bit 1
    QUALIFIED_LOCAL_TIME_SYNCHRONIZED = 0x0004  # Bit 2
    PROPOSE_TIME_UPDATE_REQUEST = 0x0008  # Bit 3
    EPOCH_YEAR_2000 = 0x0010  # Bit 4
    NON_LOGGED_TIME_CHANGE_ACTIVE = 0x0020  # Bit 5
    LOG_CONSOLIDATION_ACTIVE = 0x0040  # Bit 6


class DeviceTimeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Device Time characteristic.

    Attributes:
        base_time: Seconds since epoch (1900 or 2000 per DTStatus.EPOCH_YEAR_2000).
        time_zone: Offset in 15-minute units (sint8, -48..+56).
        dst_offset: DST offset (0=Std, 2=+0.5h, 4=+1h, 8=+2h, 255=Unknown).
        dt_status: Device Time status bitfield (Table 3.7).
        user_time: Optional seconds since epoch for user-facing display time.
        accumulated_rtc_drift: Optional accumulated RTC drift in seconds.
        next_sequence_number: Optional next time-change log sequence number.
        base_time_second_fractions: Optional sub-second fractions (1/65536 s).
    """

    base_time: int
    time_zone: int
    dst_offset: int
    dt_status: DTStatus
    user_time: int | None = None
    accumulated_rtc_drift: int | None = None
    next_sequence_number: int | None = None
    base_time_second_fractions: int | None = None


class DeviceTimeCharacteristic(BaseCharacteristic[DeviceTimeData]):
    """Device Time characteristic (0x2B90).

    org.bluetooth.characteristic.device_time

    Contains epoch-based Base_Time (uint32), Time_Zone (sint8), DST_Offset
    (uint8), and DT_Status (uint16 bitfield).  Optional fields follow when
    their corresponding feature bits are set in the DT Feature characteristic.
    """

    min_length = _MIN_LENGTH
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DeviceTimeData:
        base_time = DataParser.parse_int32(data, 0, signed=False)
        time_zone = DataParser.parse_int8(data, 4, signed=True)
        dst_offset = DataParser.parse_int8(data, 5, signed=False)
        dt_status = DTStatus(DataParser.parse_int16(data, 6, signed=False))

        offset = 8
        user_time: int | None = None
        accumulated_rtc_drift: int | None = None
        next_sequence_number: int | None = None
        base_time_second_fractions: int | None = None

        if len(data) >= offset + 4:
            user_time = DataParser.parse_int32(data, offset, signed=False)
            offset += 4

        if len(data) >= offset + 2:
            accumulated_rtc_drift = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        if len(data) >= offset + 2:
            next_sequence_number = DataParser.parse_int16(data, offset, signed=False)
            offset += 2

        if len(data) >= offset + 2:
            base_time_second_fractions = DataParser.parse_int16(data, offset, signed=False)

        return DeviceTimeData(
            base_time=base_time,
            time_zone=time_zone,
            dst_offset=dst_offset,
            dt_status=dt_status,
            user_time=user_time,
            accumulated_rtc_drift=accumulated_rtc_drift,
            next_sequence_number=next_sequence_number,
            base_time_second_fractions=base_time_second_fractions,
        )

    def _encode_value(self, data: DeviceTimeData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int32(data.base_time, signed=False))
        result.extend(DataParser.encode_int8(data.time_zone, signed=True))
        result.extend(DataParser.encode_int8(data.dst_offset, signed=False))
        result.extend(DataParser.encode_int16(int(data.dt_status), signed=False))
        if data.user_time is not None:
            result.extend(DataParser.encode_int32(data.user_time, signed=False))
        if data.accumulated_rtc_drift is not None:
            result.extend(DataParser.encode_int16(data.accumulated_rtc_drift, signed=False))
        if data.next_sequence_number is not None:
            result.extend(DataParser.encode_int16(data.next_sequence_number, signed=False))
        if data.base_time_second_fractions is not None:
            result.extend(DataParser.encode_int16(data.base_time_second_fractions, signed=False))
        return result
