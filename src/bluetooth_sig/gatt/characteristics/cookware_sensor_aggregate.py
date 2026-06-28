"""Cookware Sensor Aggregate characteristic (0x2C2D)."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class CookwareSensorAggregateValue(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Cookware Sensor Aggregate payload.

    CWS defines this value as the concatenation of participating Cookware
    Sensor Data characteristic values. Segment boundaries are described by the
    Cooking Sensor Info descriptor Aggregate Offset fields.
    """

    aggregate_data: bytes = b""


class CookwareSensorAggregateCharacteristic(BaseCharacteristic[CookwareSensorAggregateValue]):
    """Cookware Sensor Aggregate characteristic (0x2C2D).

    org.bluetooth.characteristic.cookware_sensor_aggregate
    """

    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> CookwareSensorAggregateValue:
        return CookwareSensorAggregateValue(aggregate_data=bytes(data))

    def _encode_value(self, data: CookwareSensorAggregateValue) -> bytearray:
        return bytearray(data.aggregate_data)
