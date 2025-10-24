"""Client Characteristic Configuration Descriptor implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class CCCDFlags(IntFlag):
    """CCCD (Client Characteristic Configuration Descriptor) flags."""

    NOTIFICATIONS_ENABLED = 0x0001
    INDICATIONS_ENABLED = 0x0002


class CCCDData(msgspec.Struct, frozen=True, kw_only=True):
    """CCCD (Client Characteristic Configuration Descriptor) data."""

    notifications_enabled: bool
    indications_enabled: bool


class CCCDDescriptor(BaseDescriptor):
    """Client Characteristic Configuration Descriptor (0x2902).

    Controls notification and indication settings for a characteristic.
    Critical for enabling BLE notifications and indications.
    """

    _descriptor_name = "Client Characteristic Configuration"

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> CCCDData:
        """Parse CCCD value into notification/indication flags.

        Args:
            data: Raw bytes (should be 2 bytes for uint16)

        Returns:
            CCCDData with notification/indication flags

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != 2:
            raise ValueError(f"CCCD data must be exactly 2 bytes, got {len(data)}")

        # Parse as little-endian uint16
        value = DataParser.parse_int16(data, endian="little")

        return CCCDData(
            notifications_enabled=bool(value & CCCDFlags.NOTIFICATIONS_ENABLED),
            indications_enabled=bool(value & CCCDFlags.INDICATIONS_ENABLED),
        )

    @staticmethod
    def create_enable_notifications_value() -> bytes:
        """Create value to enable notifications."""
        return CCCDFlags.NOTIFICATIONS_ENABLED.to_bytes(2, "little")

    @staticmethod
    def create_enable_indications_value() -> bytes:
        """Create value to enable indications."""
        return CCCDFlags.INDICATIONS_ENABLED.to_bytes(2, "little")

    @staticmethod
    def create_enable_both_value() -> bytes:
        """Create value to enable both notifications and indications."""
        return (CCCDFlags.NOTIFICATIONS_ENABLED | CCCDFlags.INDICATIONS_ENABLED).to_bytes(2, "little")

    @staticmethod
    def create_disable_value() -> bytes:
        """Create value to disable notifications/indications."""
        return (0).to_bytes(2, "little")

    def is_notifications_enabled(self, data: bytes) -> bool:
        """Check if notifications are enabled."""
        parsed = self._parse_descriptor_value(data)
        return parsed.notifications_enabled

    def is_indications_enabled(self, data: bytes) -> bool:
        """Check if indications are enabled."""
        parsed = self._parse_descriptor_value(data)
        return parsed.indications_enabled

    def is_any_enabled(self, data: bytes) -> bool:
        """Check if either notifications or indications are enabled."""
        parsed = self._parse_descriptor_value(data)
        return parsed.notifications_enabled or parsed.indications_enabled
