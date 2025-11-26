"""Rotational Speed characteristic implementation."""

from __future__ import annotations

from ..constants import SINT32_MAX, SINT32_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class RotationalSpeedValues:  # pylint: disable=too-few-public-methods
    """Special values for Rotational Speed characteristic per Bluetooth SIG specification."""

    VALUE_NOT_KNOWN = 0x7FFFFFFF


class RotationalSpeedCharacteristic(BaseCharacteristic):
    """Rotational Speed characteristic (0x2C09).

    org.bluetooth.characteristic.rotational_speed

    The Rotational Speed characteristic is used to represent the rotational speed of an object
    rotating around a device-specific axis.
    """

    expected_length = 4

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
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
        if raw_value == RotationalSpeedValues.VALUE_NOT_KNOWN:
            return None
        return float(raw_value)

    def encode_value(self, data: float) -> bytearray:
        """Encode rotational speed value."""
        if not SINT32_MIN <= data <= SINT32_MAX - 1:
            raise ValueError(f"Rotational speed value {data} out of valid range")
        raw_value = int(data)
        return DataParser.encode_int32(raw_value, signed=True)
