"""Server Supported Features characteristic (0x2B3A)."""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ServerFeatures(IntFlag):
    """GATT server supported feature flags."""

    EATT = 0x01


class ServerSupportedFeaturesCharacteristic(BaseCharacteristic[ServerFeatures]):
    """Server Supported Features characteristic (0x2B3A).

    org.bluetooth.characteristic.server_supported_features

    Variable-length bitfield indicating GATT features supported by the server.
    """

    allow_variable_length: bool = True
    min_length: int = 1

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ServerFeatures:
        result = 0
        for i, byte in enumerate(data):
            result |= byte << (8 * i)
        return ServerFeatures(result)

    def _encode_value(self, data: ServerFeatures) -> bytearray:
        result = bytearray()
        val = int(data)
        while val > 0:
            result.append(val & 0xFF)
            val >>= 8
        return result or bytearray([0])
