"""HID Control Point characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

# Constants per Bluetooth HID specification
HID_CONTROL_POINT_DATA_LENGTH = 1  # Fixed data length: 1 byte


class HidControlPointCommand(IntEnum):
    """HID Control Point commands."""

    SUSPEND = 0
    EXIT_SUSPEND = 1


class HidControlPointCharacteristic(BaseCharacteristic):
    """HID Control Point characteristic (0x2A4C).

    org.bluetooth.characteristic.hid_control_point

    HID Control Point characteristic.
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> HidControlPointCommand:
        """Parse HID control point data.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context.

        Returns:
            Control point command.
        """
        if len(data) != HID_CONTROL_POINT_DATA_LENGTH:
            raise ValueError(
                f"HID Control Point data must be exactly {HID_CONTROL_POINT_DATA_LENGTH} byte, got {len(data)}"
            )
        value = DataParser.parse_int8(data, 0, signed=False)
        return HidControlPointCommand(value)

    def encode_value(self, data: HidControlPointCommand) -> bytearray:
        """Encode control point command back to bytes.

        Args:
            data: Control point command to encode

        Returns:
            Encoded bytes
        """
        return DataParser.encode_int8(data.value, signed=False)
