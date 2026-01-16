"""Acceleration characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class AccelerationCharacteristic(BaseCharacteristic[float]):
    """Acceleration characteristic (0x2C06).

    org.bluetooth.characteristic.acceleration

    The Acceleration characteristic is used to represent the acceleration of an object
    along a given axis as determined by the service.
    """

    _manual_unit: str | None = "m/s²"  # Manual override due to YAML typo (metres_per_seconds_squared)

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> float | None:
        """Decode acceleration characteristic.

        Decodes a 32-bit signed integer representing acceleration in 0.001 m/s² increments
        per Bluetooth SIG Acceleration characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Acceleration in meters per second squared

        Raises:
            InsufficientDataError: If data is not exactly 4 bytes
        """
        raw_value = DataParser.parse_int32(data, 0, signed=True)
        return raw_value * 0.001

    def _encode_value(self, data: float) -> bytearray:
        """Encode acceleration value."""
        raw_value = int(data / 0.001)
        return DataParser.encode_int32(raw_value, signed=True)
