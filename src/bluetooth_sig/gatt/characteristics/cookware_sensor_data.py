"""Cookware Sensor Data characteristic (0x2C2C)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CookwareSensorDataValue(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Cookware Sensor Data payload.

    Bluetooth Assigned Numbers define this characteristic ID but do not publish
    a GSS schema yet. This parser keeps the mandatory flags field explicit and
    preserves variable-length payload bytes for vendor/spec-specific decoding.
    """

    flags: int
    sensor_payload: bytes = b""


class CookwareSensorDataCharacteristic(BaseCharacteristic[CookwareSensorDataValue]):
    """Cookware Sensor Data characteristic (0x2C2C).

    org.bluetooth.characteristic.cookware_sensor_data
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookwareSensorDataValue:
        flags = DataParser.parse_int16(data, 0, signed=False)
        payload = bytes(data[2:])
        return CookwareSensorDataValue(flags=flags, sensor_payload=payload)

    def _encode_value(self, data: CookwareSensorDataValue) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(data.flags, signed=False))
        result.extend(data.sensor_payload)
        return result
