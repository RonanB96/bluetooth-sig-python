"""Peripheral Privacy Flag characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class PeripheralPrivacyFlagCharacteristic(BaseCharacteristic[bool]):
    """Peripheral Privacy Flag characteristic (0x2A02).

    org.bluetooth.characteristic.gap.peripheral_privacy_flag

    Indicates whether privacy is enabled (True) or disabled (False).
    """

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> bool:
        """Decode the privacy flag value."""
        value = DataParser.parse_int8(data, 0, signed=False)
        return bool(value)

    def _encode_value(self, data: bool) -> bytearray:
        """Encode the privacy flag value."""
        return DataParser.encode_int8(1 if data else 0, signed=False)
