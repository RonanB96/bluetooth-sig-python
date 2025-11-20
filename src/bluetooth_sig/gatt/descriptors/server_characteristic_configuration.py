"""Server Characteristic Configuration Descriptor implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class SCCDFlags(IntFlag):
    """SCCD (Server Characteristic Configuration Descriptor) flags."""

    BROADCASTS_ENABLED = 0x0001


class SCCDData(msgspec.Struct, frozen=True, kw_only=True):
    """SCCD (Server Characteristic Configuration Descriptor) data."""

    broadcasts_enabled: bool


class ServerCharacteristicConfigurationDescriptor(BaseDescriptor):
    """Server Characteristic Configuration Descriptor (0x2903).

    Controls server-side configuration for a characteristic.
    Currently only supports broadcast enable/disable.
    """

    _writable = True  # SCCD is always writable

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> SCCDData:
        """Parse SCCD value into broadcast flags.

        Args:
            data: Raw bytes (should be 2 bytes for uint16)

        Returns:
            SCCDData with broadcast flags

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != 2:
            raise ValueError(f"SCCD data must be exactly 2 bytes, got {len(data)}")

        # Parse as little-endian uint16
        value = DataParser.parse_int16(data, endian="little")

        return SCCDData(
            broadcasts_enabled=bool(value & SCCDFlags.BROADCASTS_ENABLED),
        )

    @staticmethod
    def create_enable_broadcasts_value() -> bytes:
        """Create value to enable broadcasts."""
        return SCCDFlags.BROADCASTS_ENABLED.to_bytes(2, "little")

    @staticmethod
    def create_disable_broadcasts_value() -> bytes:
        """Create value to disable broadcasts."""
        return (0).to_bytes(2, "little")

    def is_broadcasts_enabled(self, data: bytes) -> bool:
        """Check if broadcasts are enabled."""
        parsed = self._parse_descriptor_value(data)
        return parsed.broadcasts_enabled
