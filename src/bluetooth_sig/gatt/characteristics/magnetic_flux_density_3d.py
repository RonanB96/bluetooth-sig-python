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

    def encode_value(self, data: dict[str, Any]) -> bytearray:
        """Encode magnetic flux density 3D value back to bytes.

        Args:
            data: Dictionary with 'x_axis', 'y_axis', and 'z_axis' values in Tesla

        Returns:
            Encoded bytes representing the magnetic flux density (3 x sint16, 10^-7 Tesla resolution)
        """
        if not isinstance(data, dict):
            raise TypeError("Magnetic flux density 3D data must be a dictionary")
        
        if "x_axis" not in data or "y_axis" not in data or "z_axis" not in data:
            raise ValueError("Magnetic flux density 3D data must contain 'x_axis', 'y_axis', and 'z_axis' keys")
        
        x_tesla = float(data["x_axis"])
        y_tesla = float(data["y_axis"])
        z_tesla = float(data["z_axis"])
        
        # Convert Tesla to raw values (divide by 1e-7 for 10^-7 Tesla resolution)
        x_raw = round(x_tesla / 1e-7)
        y_raw = round(y_tesla / 1e-7)
        z_raw = round(z_tesla / 1e-7)
        
        # Validate range for sint16 (-32768 to 32767)
        if not -32768 <= x_raw <= 32767:
            raise ValueError(f"X-axis value {x_raw} exceeds sint16 range")
        if not -32768 <= y_raw <= 32767:
            raise ValueError(f"Y-axis value {y_raw} exceeds sint16 range")
        if not -32768 <= z_raw <= 32767:
            raise ValueError(f"Z-axis value {z_raw} exceeds sint16 range")
        
        # Encode as 3 sint16 values (little endian)
        result = bytearray()
        result.extend(x_raw.to_bytes(2, byteorder="little", signed=True))
        result.extend(y_raw.to_bytes(2, byteorder="little", signed=True))
        result.extend(z_raw.to_bytes(2, byteorder="little", signed=True))
        
        return result
