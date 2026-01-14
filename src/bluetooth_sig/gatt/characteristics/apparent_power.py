"""Apparent Power characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class ApparentPowerCharacteristic(BaseCharacteristic[float]):
    """Apparent Power characteristic."""

    _manual_unit: str | None = "VA"  # YAML: electrical_apparent_power.volt_ampere, units.yaml: power.volt_ampere

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> float:
        """Decode the apparent power value."""
        value = DataParser.parse_int24(data, 0, signed=False)

        return value * 0.1  # Resolution 0.1 VA

    def _encode_value(self, data: float) -> bytearray:
        """Encode the apparent power value."""
        encoded = int(data / 0.1)
        return DataParser.encode_int24(encoded, signed=False)
