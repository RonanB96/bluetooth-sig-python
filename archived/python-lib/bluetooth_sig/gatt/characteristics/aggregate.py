"""Aggregate characteristic (0x2A5A)."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class AggregateCharacteristic(BaseCharacteristic[bytes]):
    """Aggregate characteristic (0x2A5A).

    org.bluetooth.characteristic.aggregate

    Concatenation of all characteristic values referenced by the
    Aggregate format descriptor. Treated as raw bytes passthrough.
    """

    min_length = 0
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> bytes:
        return bytes(data)

    def _encode_value(self, data: bytes) -> bytearray:
        return bytearray(data)
