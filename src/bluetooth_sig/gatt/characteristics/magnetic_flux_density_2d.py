"""Magnetic Flux Density 2D characteristic implementation."""

from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class MagneticFluxDensity2DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 2D characteristic.

    Represents measurements of magnetic flux density for two orthogonal axes: X and Y.
    Note that 1 x 10^-7 Tesla equals 0.001 Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 2D"
    _manual_value_type: str = (
        "dict"  # Override YAML int type since parse_value returns dict
    )

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse magnetic flux density 2D data (2 x sint16 in units of 10^-7 Tesla)."""
        if len(data) < 4:
            raise ValueError("Magnetic flux density 2D data must be at least 4 bytes")

        # Parse X-axis (first 2 bytes)
        x_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        x_tesla = x_raw * 1e-7  # Convert to Tesla

        # Parse Y-axis (next 2 bytes)
        y_raw = int.from_bytes(data[2:4], byteorder="little", signed=True)
        y_tesla = y_raw * 1e-7  # Convert to Tesla

        return {"x_axis": x_tesla, "y_axis": y_tesla, "unit": "T"}

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "T"
