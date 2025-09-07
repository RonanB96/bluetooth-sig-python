"""Magnetic Flux Density 3D characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class MagneticFluxDensity3DData:
    """Data class for magnetic flux density 3D."""

    x_axis: float  # X-axis magnetic flux density in Tesla
    y_axis: float  # Y-axis magnetic flux density in Tesla
    z_axis: float  # Z-axis magnetic flux density in Tesla
    unit: str = "T"

    def __post_init__(self):
        """Validate magnetic flux density data."""
        # Convert Tesla to raw values to validate range
        x_raw = round(self.x_axis / 1e-7)
        y_raw = round(self.y_axis / 1e-7)
        z_raw = round(self.z_axis / 1e-7)

        # Validate range for sint16 (-32768 to 32767)
        if not -32768 <= x_raw <= 32767:
            raise ValueError(f"X-axis value {x_raw} exceeds sint16 range")
        if not -32768 <= y_raw <= 32767:
            raise ValueError(f"Y-axis value {y_raw} exceeds sint16 range")
        if not -32768 <= z_raw <= 32767:
            raise ValueError(f"Z-axis value {z_raw} exceeds sint16 range")


@dataclass
class MagneticFluxDensity3DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 3D characteristic.

    Represents measurements of magnetic flux density for three orthogonal axes: X, Y, and Z.
    Note that 1 x 10^-7 Tesla equals 0.001 Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 3D"
    _manual_value_type: str = "string"  # Override since parse_value returns dataclass

    def parse_value(self, data: bytearray) -> MagneticFluxDensity3DData:
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

        return MagneticFluxDensity3DData(x_axis=x_tesla, y_axis=y_tesla, z_axis=z_tesla)

    def encode_value(
        self, data: MagneticFluxDensity3DData | dict[str, Any]
    ) -> bytearray:
        """Encode magnetic flux density 3D value back to bytes.

        Args:
            data: MagneticFluxDensity3DData instance or dict with 'x_axis', 'y_axis', and 'z_axis' values in Tesla

        Returns:
            Encoded bytes representing the magnetic flux density (3 x sint16, 10^-7 Tesla resolution)
        """
        if isinstance(data, dict):
            # Convert dict to dataclass for backward compatibility
            if "x_axis" not in data or "y_axis" not in data or "z_axis" not in data:
                raise ValueError(
                    "Magnetic flux density 3D data must contain 'x_axis', 'y_axis', and 'z_axis' keys"
                )
            data = MagneticFluxDensity3DData(
                x_axis=float(data["x_axis"]),
                y_axis=float(data["y_axis"]),
                z_axis=float(data["z_axis"]),
            )
        elif not isinstance(data, MagneticFluxDensity3DData):
            raise TypeError(
                "Magnetic flux density 3D data must be MagneticFluxDensity3DData or dictionary"
            )

        # Convert Tesla to raw values (divide by 1e-7 for 10^-7 Tesla resolution)
        x_raw = round(data.x_axis / 1e-7)
        y_raw = round(data.y_axis / 1e-7)
        z_raw = round(data.z_axis / 1e-7)

        # Encode as 3 sint16 values (little endian)
        result = bytearray()
        result.extend(x_raw.to_bytes(2, byteorder="little", signed=True))
        result.extend(y_raw.to_bytes(2, byteorder="little", signed=True))
        result.extend(z_raw.to_bytes(2, byteorder="little", signed=True))

        return result
