"""Rotational Speed characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class RotationalSpeedCharacteristic(BaseCharacteristic[float]):
    """Rotational Speed characteristic (0x2C09).

    org.bluetooth.characteristic.rotational_speed

    The Rotational Speed characteristic is used to represent the rotational speed of an object
    rotating around a device-specific axis.
    """

    _manual_unit: str | None = "RPM"  # YAML ID mismatch: has rotational_speed.*, should be angular_velocity.*

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float | None:
        """Decode rotational speed characteristic.

        Decodes a 32-bit signed integer representing speed in RPM
        per Bluetooth SIG Rotational Speed characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Rotational speed in revolutions per minute (RPM), or None if value is not known

        Raises:
            InsufficientDataError: If data is not exactly 4 bytes
        """
        raw_value = DataParser.parse_int32(data, 0, signed=True)
        return float(raw_value)

    def _encode_value(self, data: float) -> bytearray:
        """Encode rotational speed value."""
        raw_value = int(data)
        return DataParser.encode_int32(raw_value, signed=True)
