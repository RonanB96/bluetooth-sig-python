"""Device Time characteristic (0x2B90)."""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_MIN_LENGTH = 8  # year(2) + month(1) + day(1) + hours(1) + minutes(1) + seconds(1) + time_source(1)


class DeviceTimeSource(IntEnum):
    """Device Time source values."""

    UNKNOWN = 0x00
    NETWORK_TIME_PROTOCOL = 0x01
    GPS = 0x02
    RADIO_TIME_SIGNAL = 0x03
    MANUAL = 0x04
    ATOMIC_CLOCK = 0x05
    CELLULAR_NETWORK = 0x06


class DeviceTimeData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Device Time characteristic.

    Attributes:
        dt: Date and time as a Python datetime object.
        time_source: Source of time information.
    """

    dt: datetime
    time_source: DeviceTimeSource


class DeviceTimeCharacteristic(BaseCharacteristic[DeviceTimeData]):
    """Device Time characteristic (0x2B90).

    org.bluetooth.characteristic.device_time

    Contains the current date and time of the device along with
    the time source information.
    """

    min_length = _MIN_LENGTH
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DeviceTimeData:
        dt = datetime(
            year=DataParser.parse_int16(data, 0, signed=False),
            month=DataParser.parse_int8(data, 2, signed=False),
            day=DataParser.parse_int8(data, 3, signed=False),
            hour=DataParser.parse_int8(data, 4, signed=False),
            minute=DataParser.parse_int8(data, 5, signed=False),
            second=DataParser.parse_int8(data, 6, signed=False),
        )
        time_source = DeviceTimeSource(DataParser.parse_int8(data, 7, signed=False))

        return DeviceTimeData(dt=dt, time_source=time_source)

    def _encode_value(self, data: DeviceTimeData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(data.dt.year, signed=False))
        result.extend(DataParser.encode_int8(data.dt.month, signed=False))
        result.extend(DataParser.encode_int8(data.dt.day, signed=False))
        result.extend(DataParser.encode_int8(data.dt.hour, signed=False))
        result.extend(DataParser.encode_int8(data.dt.minute, signed=False))
        result.extend(DataParser.encode_int8(data.dt.second, signed=False))
        result.extend(DataParser.encode_int8(int(data.time_source), signed=False))
        return result
