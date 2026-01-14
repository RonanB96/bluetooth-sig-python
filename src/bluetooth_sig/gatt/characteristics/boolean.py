"""Boolean characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from ..context import CharacteristicContext
from .base import BaseCharacteristic


class BooleanCharacteristic(BaseCharacteristic[bool]):
    """Boolean characteristic (0x2AE2).

    org.bluetooth.characteristic.boolean

    The Boolean characteristic is used to represent predefined Boolean values (0 or 1).
    """

    _manual_value_type = ValueType.BOOL
    expected_length = 1

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> bool:
        """Parse boolean value.

        Args:
            data: Raw bytearray from BLE characteristic (1 byte, validated by base class).
            ctx: Optional CharacteristicContext.

        Returns:
            True if value is 1, False if value is 0.
        """
        return bool(data[0])

    def _encode_value(self, data: bool) -> bytearray:
        """Encode boolean value back to bytes.

        Args:
            data: Boolean value to encode

        Returns:
            Encoded bytes (1 byte: 0x01 for True, 0x00 for False)
        """
        return bytearray([1 if data else 0])
