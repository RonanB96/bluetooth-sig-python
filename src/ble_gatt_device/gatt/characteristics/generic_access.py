"""Generic Access Service characteristics."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic."""

    _characteristic_name: str = "Device Name"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "string"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> str:
        """Parse device name string."""
        return self._parse_utf8_string(data)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class AppearanceCharacteristic(BaseCharacteristic):
    """Appearance characteristic."""

    _characteristic_name: str = "Appearance"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "int"
        super().__post_init__()

    def parse_value(self, data: bytearray) -> int:
        """Parse appearance value (uint16)."""
        if len(data) < 2:
            raise ValueError("Appearance data must be at least 2 bytes")

        return int.from_bytes(data[:2], byteorder="little", signed=False)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""
