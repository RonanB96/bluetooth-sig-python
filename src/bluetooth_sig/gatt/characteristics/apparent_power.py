"""Apparent Power characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser

# Special value constants for Apparent Power characteristic
VALUE_NOT_VALID = 0xFFFFFE  # Indicates value is not valid
VALUE_UNKNOWN = 0xFFFFFF  # Indicates value is not known


class ApparentPowerCharacteristic(BaseCharacteristic):
    """Apparent Power characteristic."""

    _manual_unit: str | None = "VA"  # YAML: electrical_apparent_power.volt_ampere, units.yaml: power.volt_ampere

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
        """Decode the apparent power value."""
        value = DataParser.parse_int24(data, 0, signed=False)

        if value == VALUE_NOT_VALID:
            return None  # Value is not valid
        if value == VALUE_UNKNOWN:
            return None  # Value is not known

        return value * 0.1  # Resolution 0.1 VA

    def encode_value(self, data: float) -> bytearray:
        """Encode the apparent power value."""
        encoded = int(data / 0.1)
        return DataParser.encode_int24(encoded, signed=False)
