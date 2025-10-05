"""Magnetic Flux Density 3D characteristic implementation."""

from __future__ import annotations

from typing import Any

from ...types.gatt_enums import ValueType
from .base import BaseCharacteristic
from .templates import VectorData
from .utils import DataParser


class MagneticFluxDensity3DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 3D characteristic.

    Represents measurements of magnetic flux density for three
    orthogonal axes: X, Y, and Z. Note that 1 x 10^-7 Tesla equals 0.001
    Gauss.

    Format: 3 x sint16 (6 bytes total) with 1e-7 Tesla resolution.
    """

    _characteristic_name: str | None = "Magnetic Flux Density - 3D"
    _manual_value_type: ValueType | str | None = ValueType.STRING  # Override since decode_value returns dict
    _manual_unit: str | None = "T"  # Override template's "units" default

    _vector_components: list[str] = ["x_axis", "y_axis", "z_axis"]
    resolution: float = 1e-7

    def decode_value(self, data: bytearray, ctx: Any | None = None) -> VectorData:
        """Parse 3D magnetic flux density (3 x sint16 with resolution)."""
        if len(data) < 6:
            raise ValueError("Insufficient data for 3D magnetic flux density (need 6 bytes)")

        x_raw = DataParser.parse_int16(data, 0, signed=True)
        y_raw = DataParser.parse_int16(data, 2, signed=True)
        z_raw = DataParser.parse_int16(data, 4, signed=True)

        return VectorData(
            x_axis=x_raw * self.resolution, y_axis=y_raw * self.resolution, z_axis=z_raw * self.resolution
        )

    def encode_value(self, data: VectorData) -> bytearray:
        """Encode 3D magnetic flux density."""
        x_raw = int(data.x_axis / self.resolution)
        y_raw = int(data.y_axis / self.resolution)
        z_raw = int(data.z_axis / self.resolution)

        result = bytearray()
        result.extend(DataParser.encode_int16(x_raw, signed=True))
        result.extend(DataParser.encode_int16(y_raw, signed=True))
        result.extend(DataParser.encode_int16(z_raw, signed=True))
        return result
