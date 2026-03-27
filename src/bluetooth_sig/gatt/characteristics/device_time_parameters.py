"""Device Time Parameters characteristic (0x2B8F)."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class TimeUpdateFlags(IntFlag):
    """Device Time Parameters time update flags (uint8)."""

    TIME_UPDATE_PENDING = 0x01
    TIME_UPDATE_IN_PROGRESS = 0x02
    TIME_ZONE_UPDATE_PENDING = 0x04
    DST_UPDATE_PENDING = 0x08


class TimeProperties(IntFlag):
    """Device Time Parameters time properties (uint8)."""

    TIME_SOURCE_SET = 0x01
    TIME_ACCURACY_KNOWN = 0x02
    UTC_ALIGNED = 0x04


class DeviceTimeParametersData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from Device Time Parameters characteristic."""

    time_update_flags: TimeUpdateFlags
    time_accuracy: int
    time_properties: TimeProperties


class DeviceTimeParametersCharacteristic(BaseCharacteristic[DeviceTimeParametersData]):
    """Device Time Parameters characteristic (0x2B8F).

    org.bluetooth.characteristic.device_time_parameters

    Contains time-update configuration parameters.
    """

    expected_length: int = 3

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DeviceTimeParametersData:
        time_update_flags = DataParser.parse_int8(data, 0, signed=False)
        time_accuracy = DataParser.parse_int8(data, 1, signed=False)
        time_properties = DataParser.parse_int8(data, 2, signed=False)

        return DeviceTimeParametersData(
            time_update_flags=TimeUpdateFlags(time_update_flags),
            time_accuracy=time_accuracy,
            time_properties=TimeProperties(time_properties),
        )

    def _encode_value(self, data: DeviceTimeParametersData) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.time_update_flags), signed=False))
        result.extend(DataParser.encode_int8(data.time_accuracy, signed=False))
        result.extend(DataParser.encode_int8(int(data.time_properties), signed=False))
        return result
