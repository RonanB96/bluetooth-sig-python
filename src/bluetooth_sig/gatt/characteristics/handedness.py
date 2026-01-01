"""Handedness characteristic (0x2B4A)."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.exceptions import ValueRangeError

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

    expected_length: int | None = 1

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> Handedness:
        """Decode handedness from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            Handedness enum value

        Raises:
            ValueRangeError: If value is invalid (not 0x00-0x03)
        """
        handedness_value = int(data[0])
        if handedness_value > Handedness.UNSPECIFIED:
            raise ValueRangeError("Handedness", handedness_value, Handedness.LEFT_HANDED, Handedness.UNSPECIFIED)
        return Handedness(handedness_value)

    def encode_value(self, data: Handedness) -> bytearray:
        """Encode handedness to raw bytes.

        Args:
            data: Handedness enum value

        Returns:
            bytearray: Encoded bytes
        """
        return bytearray([data.value])
