"""Magnetic Flux Density 2D characteristic implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base import BaseCharacteristic


@dataclass
class MagneticFluxDensity2DData:
    """Data class for magnetic flux density 2D."""

    x_axis: float  # X-axis magnetic flux density in Tesla
    y_axis: float  # Y-axis magnetic flux density in Tesla
    unit: str = "T"

    def __post_init__(self):
        """Validate magnetic flux density data."""
        # Convert Tesla to raw values to validate range
        x_raw = round(self.x_axis / 1e-7)
        y_raw = round(self.y_axis / 1e-7)

        # Validate range for sint16 (-32768 to 32767)
        if not -32768 <= x_raw <= 32767:
            raise ValueError(f"X-axis value {x_raw} exceeds sint16 range")
        if not -32768 <= y_raw <= 32767:
            raise ValueError(f"Y-axis value {y_raw} exceeds sint16 range")


@dataclass
class MagneticFluxDensity2DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 2D characteristic.

    Represents measurements of magnetic flux density for two orthogonal axes: X and Y.
    Note that 1 x 10^-7 Tesla equals 0.001 Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 2D"
    _manual_value_type: str = "string"  # Override since parse_value returns dataclass

    def parse_value(self, data: bytearray) -> MagneticFluxDensity2DData:
        """Parse magnetic flux density 2D data (2 x sint16 in units of 10^-7 Tesla)."""
        if len(data) < 4:
            raise ValueError("Magnetic flux density 2D data must be at least 4 bytes")

        # Parse X-axis (first 2 bytes)
        x_raw = int.from_bytes(data[:2], byteorder="little", signed=True)
        x_tesla = x_raw * 1e-7  # Convert to Tesla

        # Parse Y-axis (next 2 bytes)
        y_raw = int.from_bytes(data[2:4], byteorder="little", signed=True)
        y_tesla = y_raw * 1e-7  # Convert to Tesla

        return MagneticFluxDensity2DData(x_axis=x_tesla, y_axis=y_tesla)

    def encode_value(self, data: MagneticFluxDensity2DData) -> bytearray:
        """Encode magnetic flux density 2D value back to bytes.

        Args:
            data: MagneticFluxDensity2DData instance with 'x_axis' and 'y_axis' values in Tesla

        Returns:
            Encoded bytes representing the magnetic flux density (2 x sint16, 10^-7 Tesla resolution)
        """
        if not isinstance(data, MagneticFluxDensity2DData):
            raise TypeError(
                f"Magnetic flux density 2D data must be a MagneticFluxDensity2DData, "
                f"got {type(data).__name__}"
            )
            # Convert Tesla to raw values (divide by 1e-7 for 10^-7 Tesla resolution)
        x_raw = round(data.x_axis / 1e-7)
        y_raw = round(data.y_axis / 1e-7)

        # Validate range for sint16 (-32768 to 32767)
        for name, value in [("x_axis", x_raw), ("y_axis", y_raw)]:
            if not -32768 <= value <= 32767:
                raise ValueError(f"Magnetic flux density {name} value {value} exceeds sint16 range")

        # Encode as 2 sint16 values (little endian)
        result = bytearray()
        result.extend(x_raw.to_bytes(2, byteorder="little", signed=True))
        result.extend(y_raw.to_bytes(2, byteorder="little", signed=True))

        return result
