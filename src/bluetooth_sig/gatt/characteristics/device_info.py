"""Device Information Service characteristics."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class ManufacturerNameStringCharacteristic(BaseCharacteristic):
    """Manufacturer Name String characteristic."""

    _characteristic_name: str = "Manufacturer Name String"

    def parse_value(self, data: bytearray) -> str:
        """Parse manufacturer name string."""
        return self._parse_utf8_string(data)


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")
    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class ModelNumberStringCharacteristic(BaseCharacteristic):
    """Model Number String characteristic."""

    _characteristic_name: str = "Model Number String"

    def parse_value(self, data: bytearray) -> str:
        """Parse model number string."""
        return self._parse_utf8_string(data)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class SerialNumberStringCharacteristic(BaseCharacteristic):
    """Serial Number String characteristic."""

    _characteristic_name: str = "Serial Number String"

    def parse_value(self, data: bytearray) -> str:
        """Parse serial number string."""
        return self._parse_utf8_string(data)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class FirmwareRevisionStringCharacteristic(BaseCharacteristic):
    """Firmware Revision String characteristic."""

    _characteristic_name: str = "Firmware Revision String"

    def parse_value(self, data: bytearray) -> str:
        """Parse firmware revision string."""
        return self._parse_utf8_string(data)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class HardwareRevisionStringCharacteristic(BaseCharacteristic):
    """Hardware Revision String characteristic."""

    _characteristic_name: str = "Hardware Revision String"

    def parse_value(self, data: bytearray) -> str:
        """Parse hardware revision string."""
        return self._parse_utf8_string(data)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class SoftwareRevisionStringCharacteristic(BaseCharacteristic):
    """Software Revision String characteristic."""

    _characteristic_name: str = "Software Revision String"

    def parse_value(self, data: bytearray) -> str:
        """Parse software revision string."""
        return self._parse_utf8_string(data)

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""
