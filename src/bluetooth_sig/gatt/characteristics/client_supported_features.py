"""Client Supported Features characteristic (0x2B29)."""

from __future__ import annotations

from enum import IntFlag

from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ClientFeatures(IntFlag):
    """GATT client supported feature flags."""

    ROBUST_CACHING = 0x01
    EATT = 0x02
    MULTIPLE_HANDLE_VALUE_NOTIFICATIONS = 0x04


class ClientSupportedFeaturesCharacteristic(BaseCharacteristic[ClientFeatures]):
    """Client Supported Features characteristic (0x2B29).

    org.bluetooth.characteristic.client_supported_features

    Variable-length bitfield indicating GATT features supported by the client.
    """

    allow_variable_length: bool = True
    min_length: int = 1

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> ClientFeatures:
        result = 0
        for i, byte in enumerate(data):
            result |= byte << (8 * i)
        return ClientFeatures(result)

    def _encode_value(self, data: ClientFeatures) -> bytearray:
        result = bytearray()
        val = int(data)
        while val > 0:
            result.append(val & 0xFF)
            val >>= 8
        return result or bytearray([0])
