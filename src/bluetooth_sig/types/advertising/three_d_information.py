"""3D Information Data (AD 0x3D, CSS Part A §1.13).

Decodes the 3D Information Data AD type used for 3D display
synchronisation between a 3D display and 3D glasses.
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from bluetooth_sig.gatt.characteristics.utils import DataParser


class ThreeDInformationFlags(IntFlag):
    """3D Information Data flags byte (CSS Part A §1.13).

    Bit assignments from the 3D Synchronisation Profile specification.
    """

    ASSOCIATION_NOTIFICATION = 0x01  # Bit 0: send association notification
    BATTERY_LEVEL_REPORTING = 0x02   # Bit 1: device reports battery level
    SEND_BATTERY_ON_STARTUP = 0x04   # Bit 2: send battery level on startup
    FACTORY_TEST_MODE = 0x80         # Bit 7: factory test mode enabled


class ThreeDInformationData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed 3D Information Data for 3D display synchronisation (CSS Part A, §1.13).

    Format: flags (1 byte) + path_loss_threshold (1 byte).

    Attributes:
        flags: Raw flags for reference and bitwise queries.
        path_loss_threshold: Path-loss threshold in dBm for proximity detection.

    """

    flags: ThreeDInformationFlags = ThreeDInformationFlags(0)
    path_loss_threshold: int = 0

    @property
    def association_notification(self) -> bool:
        """Whether association notification is enabled (bit 0)."""
        return bool(self.flags & ThreeDInformationFlags.ASSOCIATION_NOTIFICATION)

    @property
    def battery_level_reporting(self) -> bool:
        """Whether battery level reporting is enabled (bit 1)."""
        return bool(self.flags & ThreeDInformationFlags.BATTERY_LEVEL_REPORTING)

    @property
    def send_battery_on_startup(self) -> bool:
        """Whether battery level is sent on startup (bit 2)."""
        return bool(self.flags & ThreeDInformationFlags.SEND_BATTERY_ON_STARTUP)

    @property
    def factory_test_mode(self) -> bool:
        """Whether factory test mode is enabled (bit 7)."""
        return bool(self.flags & ThreeDInformationFlags.FACTORY_TEST_MODE)

    @classmethod
    def decode(cls, data: bytes | bytearray) -> ThreeDInformationData:
        """Decode 3D Information Data AD.

        DataParser raises ``InsufficientDataError`` if fewer than 2 bytes
        are available.

        Args:
            data: Raw AD data bytes (excluding length and AD type).

        Returns:
            Parsed ThreeDInformationData.

        """
        flags = ThreeDInformationFlags(DataParser.parse_int8(data, 0, signed=False))
        path_loss = DataParser.parse_int8(data, 1, signed=False)

        return cls(flags=flags, path_loss_threshold=path_loss)


__all__ = [
    "ThreeDInformationData",
    "ThreeDInformationFlags",
]
