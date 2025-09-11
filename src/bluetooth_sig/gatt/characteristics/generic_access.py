"""Generic Access Service characteristics."""

from dataclasses import dataclass

from .base import BaseCharacteristic
from .utils import DataParser


@dataclass
class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic."""

    _characteristic_name: str = "Device Name"

    def decode_value(self, data: bytearray) -> str:
        """Parse device name string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
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

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class AppearanceCharacteristic(BaseCharacteristic):
    """Appearance characteristic."""

    _characteristic_name: str = "Appearance"

    def decode_value(self, data: bytearray) -> int:
        """Parse appearance value (uint16)."""
        if len(data) < 2:
            raise ValueError("Appearance data must be at least 2 bytes")

        return int.from_bytes(data[:2], byteorder="little", signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Encode appearance value back to bytes.

        Args:
            data: Appearance value as integer

        Returns:
            Encoded bytes representing the appearance
        """
        appearance = int(data)
        return DataParser.encode_int16(appearance, signed=False)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""
