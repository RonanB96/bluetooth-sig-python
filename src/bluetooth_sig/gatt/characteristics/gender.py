"""Gender characteristic (0x2A8C)."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.gatt.context import CharacteristicContext

from .base import BaseCharacteristic


class Gender(IntEnum):
    """Gender enumeration."""

    MALE = 0
    FEMALE = 1
    UNSPECIFIED = 2


class GenderCharacteristic(BaseCharacteristic):
    """Gender characteristic (0x2A8C).

    org.bluetooth.characteristic.gender

    The Gender characteristic is used to represent the gender of a user.
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> Gender:
        """Decode gender from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            Gender enum value

        Raises:
            ValueError: If data length is not exactly 1 byte or value is invalid
        """
        if len(data) != 1:
            raise ValueError(f"Gender requires exactly 1 byte, got {len(data)}")

        gender_value = int(data[0])
        try:
            return Gender(gender_value)
        except ValueError as e:
            raise ValueError(f"Invalid Gender value: {gender_value} (valid range: 0-2)") from e

    def encode_value(self, data: Gender) -> bytearray:
        """Encode gender to raw bytes.

        Args:
            data: Gender enum value

        Returns:
            bytearray: Encoded bytes
        """
        return bytearray([data.value])
