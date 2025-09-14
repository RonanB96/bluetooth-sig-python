"""Device Information Service characteristics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic
from .utils import DataParser


@dataclass
class ManufacturerNameStringCharacteristic(BaseCharacteristic):
    """Manufacturer Name String characteristic."""

    _characteristic_name: str = "Manufacturer Name String"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse manufacturer name string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode string back to bytes.

        Args:
            data: String to encode

        Returns:
            Encoded UTF-8 bytes representing the manufacturer name
        """
        if isinstance(data, str):
            return bytearray(data.encode("utf-8"))
        raise TypeError(f"Expected str, got {type(data)}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class ModelNumberStringCharacteristic(BaseCharacteristic):
    """Model Number String characteristic."""

    _characteristic_name: str = "Model Number String"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse model number string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode string back to bytes.

        Args:
            data: String to encode

        Returns:
            Encoded UTF-8 bytes representing the model number
        """
        if isinstance(data, str):
            return bytearray(data.encode("utf-8"))
        raise TypeError(f"Expected str, got {type(data)}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class SerialNumberStringCharacteristic(BaseCharacteristic):
    """Serial Number String characteristic."""

    _characteristic_name: str = "Serial Number String"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse serial number string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode string back to bytes.

        Args:
            data: String to encode

        Returns:
            Encoded UTF-8 bytes representing the serial number
        """
        if isinstance(data, str):
            return bytearray(data.encode("utf-8"))
        raise TypeError(f"Expected str, got {type(data)}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class FirmwareRevisionStringCharacteristic(BaseCharacteristic):
    """Firmware Revision String characteristic."""

    _characteristic_name: str = "Firmware Revision String"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse firmware revision string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode string back to bytes.

        Args:
            data: String to encode

        Returns:
            Encoded UTF-8 bytes representing the firmware revision
        """
        if isinstance(data, str):
            return bytearray(data.encode("utf-8"))
        raise TypeError(f"Expected str, got {type(data)}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class HardwareRevisionStringCharacteristic(BaseCharacteristic):
    """Hardware Revision String characteristic."""

    _characteristic_name: str = "Hardware Revision String"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse hardware revision string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode string back to bytes.

        Args:
            data: String to encode

        Returns:
            Encoded UTF-8 bytes representing the hardware revision
        """
        if isinstance(data, str):
            return bytearray(data.encode("utf-8"))
        raise TypeError(f"Expected str, got {type(data)}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""


@dataclass
class SoftwareRevisionStringCharacteristic(BaseCharacteristic):
    """Software Revision String characteristic."""

    _characteristic_name: str = "Software Revision String"

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> str:
        """Parse software revision string."""
        return DataParser.parse_utf8_string(data)

    def encode_value(self, data: str) -> bytearray:
        """Encode string back to bytes.

        Args:
            data: String to encode

        Returns:
            Encoded UTF-8 bytes representing the software revision
        """
        if isinstance(data, str):
            return bytearray(data.encode("utf-8"))
        raise TypeError(f"Expected str, got {type(data)}")

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return ""
