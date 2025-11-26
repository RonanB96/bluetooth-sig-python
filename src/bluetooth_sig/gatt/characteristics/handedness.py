"""Handedness characteristic (0x2B4A)."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.gatt.context import CharacteristicContext

from .base import BaseCharacteristic


class Handedness(IntEnum):
    """Handedness enumeration."""

    LEFT_HANDED = 0x00
    RIGHT_HANDED = 0x01
    AMBIDEXTROUS = 0x02
    UNSPECIFIED = 0x03


class HandednessCharacteristic(BaseCharacteristic):
    """Handedness characteristic (0x2B4A).

    org.bluetooth.characteristic.handedness

    The Handedness characteristic is used to represent the handedness of a user.
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> Handedness:
        """Decode handedness from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            Handedness enum value

        Raises:
            ValueError: If data length is not exactly 1 byte or value is invalid
        """
        if len(data) != 1:
            raise ValueError(f"Handedness requires exactly 1 byte, got {len(data)}")

        handedness_value = int(data[0])
        try:
            return Handedness(handedness_value)
        except ValueError as e:
            raise ValueError(f"Invalid Handedness value: {handedness_value} (valid range: 0x00-0x03)") from e

    def encode_value(self, data: Handedness) -> bytearray:
        """Encode handedness to raw bytes.

        Args:
            data: Handedness enum value

        Returns:
            bytearray: Encoded bytes
        """
        return bytearray([data.value])
