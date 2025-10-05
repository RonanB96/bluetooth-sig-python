"""Generic Access Service characteristics."""

from __future__ import annotations

from typing import Any

from .base import BaseCharacteristic
from .utils import DataParser


class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic."""

    _characteristic_name: str = "Device Name"
    _manual_value_type = "string"  # Override since decode_value returns str

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse device name string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: Any) -> bytearray:
        """Encode device name value back to bytes.

        Args:
            data: Device name as string

        Returns:
            Encoded bytes representing the device name (UTF-8)
        """
        if not isinstance(data, str):
            raise TypeError("Device name must be a string")

        # Encode as UTF-8 bytes
        return bytearray(data.encode("utf-8"))


class AppearanceCharacteristic(BaseCharacteristic):
    """Appearance characteristic."""

    _characteristic_name: str = "Appearance"
    _manual_value_type = "int"  # Override since decode_value returns int

    min_length = 2  # Appearance(2) fixed length
    max_length = 2  # Appearance(2) fixed length
    allow_variable_length: bool = False  # Fixed length

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> int:
        """Parse appearance value (uint16)."""
        return DataParser.parse_int16(data, 0, signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode appearance value back to bytes.

        Args:
            data: Appearance value as integer

        Returns:
            Encoded bytes representing the appearance
        """
        appearance = int(data)
        return DataParser.encode_int16(appearance, signed=False)
