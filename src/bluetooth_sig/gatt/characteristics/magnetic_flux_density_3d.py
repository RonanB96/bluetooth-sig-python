"""Magnetic Flux Density 3D characteristic implementation."""

from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class MagneticFluxDensity3DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 3D characteristic.

    Represents measurements of magnetic flux density for three orthogonal axes: X, Y, and Z.
    Note that 1 x 10^-7 Tesla equals 0.001 Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 3D"
    _manual_value_type: str = (
        "dict"  # Override YAML int type since parse_value returns dict
    )

    def parse_value(self, data: bytearray) -> dict[str, Any]:
        """Parse magnetic flux density 3D data (3 x sint16 in units of 10^-7 Tesla)."""
        if len(data) < 6:
            raise ValueError("Magnetic flux density 3D data must be at least 6 bytes")

        # Parse X-axis (first 2 bytes)
        x_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        x_tesla = x_raw * 1e-7  # Convert to Tesla

        # Parse Y-axis (next 2 bytes)
        y_raw = int.from_bytes(data[2:4], byteorder="little", signed=True)
        y_tesla = y_raw * 1e-7  # Convert to Tesla

        # Parse Z-axis (next 2 bytes)
        z_raw = int.from_bytes(data[4:6], byteorder="little", signed=True)
        z_tesla = z_raw * 1e-7  # Convert to Tesla

        return {"x_axis": x_tesla, "y_axis": y_tesla, "z_axis": z_tesla, "unit": "T"}


    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError("encode_value not yet implemented for this characteristic")