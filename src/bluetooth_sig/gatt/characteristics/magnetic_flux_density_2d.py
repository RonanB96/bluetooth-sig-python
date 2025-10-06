"""Magnetic Flux Density 2D characteristic implementation."""

from __future__ import annotations

from typing import Any

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import Vector2DData
from .utils import DataParser


class MagneticFluxDensity2DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 2D characteristic.

    Represents measurements of magnetic flux density for two orthogonal
    axes: X and Y. Note that 1 x 10^-7 Tesla equals 0.001 Gauss.

    Format: 2 x sint16 (4 bytes total) with 1e-7 Tesla resolution.
    """

    _characteristic_name: str | None = "Magnetic Flux Density - 2D"
    # Override YAML since decode_value returns structured dict
    _manual_value_type: ValueType | str | None = ValueType.STRING  # Override since decode_value returns dict
    _manual_unit: str | None = "T"  # Tesla

    _vector_components: list[str] = ["x_axis", "y_axis"]
    resolution: float = 1e-7

    def decode_value(self, data: bytearray, _ctx: Any | None = None) -> Vector2DData:
        """Parse 2D magnetic flux density (2 x sint16 with resolution)."""
        if len(data) < 4:
            raise ValueError("Insufficient data for 2D magnetic flux density (need 4 bytes)")

        x_raw = DataParser.parse_int16(data, 0, signed=True)
        y_raw = DataParser.parse_int16(data, 2, signed=True)

        return Vector2DData(x_axis=x_raw * self.resolution, y_axis=y_raw * self.resolution)

    def encode_value(self, data: Vector2DData) -> bytearray:
        """Encode 2D magnetic flux density."""
        x_raw = int(data.x_axis / self.resolution)
        y_raw = int(data.y_axis / self.resolution)

        result = bytearray()
        result.extend(DataParser.encode_int16(x_raw, signed=True))
        result.extend(DataParser.encode_int16(y_raw, signed=True))
        return result
