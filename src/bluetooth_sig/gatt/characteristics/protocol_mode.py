"""Protocol Mode characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Constants per Bluetooth HID specification
PROTOCOL_MODE_DATA_LENGTH = 1  # Fixed data length: 1 byte


class ProtocolMode(IntEnum):
    """Protocol Mode values."""

    BOOT_PROTOCOL = 0
    REPORT_PROTOCOL = 1


class ProtocolModeCharacteristic(BaseCharacteristic):
    """Protocol Mode characteristic (0x2A4E).

    org.bluetooth.characteristic.protocol_mode

    Protocol Mode characteristic.
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> ProtocolMode:
        """Parse protocol mode data.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context.

        Returns:
            Protocol mode.
        """
        if len(data) != PROTOCOL_MODE_DATA_LENGTH:
            raise ValueError(f"Protocol Mode data must be exactly {PROTOCOL_MODE_DATA_LENGTH} byte, got {len(data)}")
        value = DataParser.parse_int8(data, 0, signed=False)
        return ProtocolMode(value)

    def encode_value(self, data: ProtocolMode) -> bytearray:
        """Encode protocol mode back to bytes.

        Args:
            data: Protocol mode to encode

        Returns:
            Encoded bytes
        """
        return DataParser.encode_int8(data.value, signed=False)
