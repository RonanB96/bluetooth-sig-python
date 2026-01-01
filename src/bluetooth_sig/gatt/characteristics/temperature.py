"""Temperature characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


# Special value constants for Temperature characteristic
class TemperatureValues:  # pylint: disable=too-few-public-methods
    """Special values for Temperature characteristic per Bluetooth SIG specification."""

    VALUE_UNKNOWN = -32768  # Indicates value is not known (as sint16, 0x8000)


class TemperatureCharacteristic(BaseCharacteristic):
    """Temperature characteristic (0x2A6E).

    org.bluetooth.characteristic.temperature

    Temperature measurement characteristic.
    """

    expected_type: type | None = float  # Allows both float and None (for unknown value)

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
        """Decode temperature characteristic.

        Decodes a 16-bit signed integer representing temperature in 0.01°C increments
        per Bluetooth SIG Temperature characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 2 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Temperature in degrees Celsius, or None if value is unknown (-32768)

        Raises:
            InsufficientDataError: If data is not exactly 2 bytes
        """
        raw_value = DataParser.parse_int16(data, 0, signed=True)
        if raw_value == TemperatureValues.VALUE_UNKNOWN:
            return None
        return raw_value * 0.01

    def encode_value(self, data: float) -> bytearray:
        """Encode temperature value."""
        raw_value = int(data / 0.01)
        return DataParser.encode_int16(raw_value, signed=True)
