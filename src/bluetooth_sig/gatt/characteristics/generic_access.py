"""Generic Access Service characteristics."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic."""

    _characteristic_name: str = "Device Name"

    def parse_value(self, data: bytearray) -> str:
        """Parse device name string."""
        return self._parse_utf8_string(data)

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class AppearanceCharacteristic(BaseCharacteristic):
    """Appearance characteristic."""

    _characteristic_name: str = "Appearance"

    def parse_value(self, data: bytearray) -> int:
        """Parse appearance value (uint16)."""
        if len(data) < 2:
            raise ValueError("Appearance data must be at least 2 bytes")

        return int.from_bytes(data[:2], byteorder="little", signed=False)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""
