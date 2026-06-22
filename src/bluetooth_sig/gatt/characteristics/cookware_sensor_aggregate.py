"""Cookware Sensor Aggregate characteristic (0x2C2D)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class CookwareSensorAggregateValue(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Cookware Sensor Aggregate payload.

    Bluetooth Assigned Numbers define this characteristic ID but do not publish
    a GSS schema yet. The parser preserves the mandatory flags field and
    variable-length aggregate payload for higher-layer interpretation.
    """

    flags: int
    aggregate_payload: bytes = b""


class CookwareSensorAggregateCharacteristic(BaseCharacteristic[CookwareSensorAggregateValue]):
    """Cookware Sensor Aggregate characteristic (0x2C2D).

    org.bluetooth.characteristic.cookware_sensor_aggregate
    """

    min_length = 2
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookwareSensorAggregateValue:
        flags = DataParser.parse_int16(data, 0, signed=False)
        payload = bytes(data[2:])
        return CookwareSensorAggregateValue(flags=flags, aggregate_payload=payload)

    def _encode_value(self, data: CookwareSensorAggregateValue) -> bytearray:
        result = bytearray()
        result.extend(DataParser.encode_int16(data.flags, signed=False))
        result.extend(data.aggregate_payload)
        return result
