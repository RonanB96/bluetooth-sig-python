"""Humidity characteristic implementation."""

from __future__ import annotations

from bluetooth_sig.gatt.constants import PERCENTAGE_MAX

from ...types.gatt_enums import ValueType
from ...types.units import PercentageUnit
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


# Special value constants for Humidity characteristic
class HumidityValues:  # pylint: disable=too-few-public-methods
    """Special values for Humidity characteristic per Bluetooth SIG specification."""

    VALUE_UNKNOWN = 0xFFFF  # Indicates value is not known


class HumidityCharacteristic(BaseCharacteristic):
    """Humidity characteristic (0x2A6F).

    org.bluetooth.characteristic.humidity

    Humidity measurement characteristic.
    """

    # Override YAML int type since decode_value returns float
    _manual_value_type: ValueType | str | None = ValueType.FLOAT
    _manual_unit: str | None = PercentageUnit.PERCENT.value  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01% resolution

    # Validation attributes
    expected_length: int = 2  # uint16
    min_value: float = 0.0
    max_value: float = PERCENTAGE_MAX  # 100% humidity
    expected_type: type = float

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
        """Decode humidity characteristic.

        Decodes a 16-bit unsigned integer representing humidity in 0.01% increments
        per Bluetooth SIG Humidity characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 2 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Humidity percentage (0.00% to 100.00%), or None if value is unknown (0xFFFF)

        Raises:
            InsufficientDataError: If data is not exactly 2 bytes
        """
        raw_value = DataParser.parse_int16(data, 0, signed=False)
        if raw_value == HumidityValues.VALUE_UNKNOWN:
            return None
        return raw_value * 0.01

    def encode_value(self, data: float) -> bytearray:
        """Encode humidity value."""
        raw_value = int(data / 0.01)
        return DataParser.encode_int16(raw_value, signed=False)
