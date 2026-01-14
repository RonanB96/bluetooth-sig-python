"""Reconnection Address characteristic implementation."""

from __future__ import annotations

from ...types.address import bytes_to_mac_address, mac_address_to_bytes
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class ReconnectionAddressCharacteristic(BaseCharacteristic[str]):
    """Reconnection Address characteristic (0x2A03).

    org.bluetooth.characteristic.gap.reconnection_address

    Contains a 48-bit Bluetooth device address for reconnection.
    """

    expected_length = 6

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> str:
        """Parse BD_ADDR to colon-separated hex string.

        Args:
            data: Raw bytearray (6 bytes).
            ctx: Optional CharacteristicContext.

        Returns:
            BD_ADDR as string (e.g., "AA:BB:CC:DD:EE:FF").
        """
        return bytes_to_mac_address(data)

    def _encode_value(self, data: str) -> bytearray:
        """Encode BD_ADDR from colon-separated hex string.

        Args:
            data: BD_ADDR string (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            Encoded bytes (6 bytes validated by BaseCharacteristic)
        """
        return bytearray(mac_address_to_bytes(data))
