"""Magnetic Flux Density 3D characteristic implementation."""

from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseCharacteristic


@dataclass
class MagneticFluxDensity3DCharacteristic(BaseCharacteristic):
    """Magnetic flux density 3D characteristic.

    Represents measurements of magnetic flux density for three orthogonal axes: X, Y, and Z.
    Note that 1 x 10^-7 Tesla equals 0.001 Gauss.
    """

    _characteristic_name: str = "Magnetic Flux Density - 3D"

    def __post_init__(self):
        """Initialize with specific value type."""
        self.value_type = "string"  # JSON string representation
        super().__post_init__()

    def parse_value(self, data: bytearray) -> Dict[str, Any]:
        """Parse magnetic flux density 3D data (3 x sint16 in units of 10^-7 Tesla).

        Args:
            data: Raw bytes from the characteristic read (6 bytes minimum)

        Returns:
            Dictionary containing X, Y, and Z axis flux density values in Tesla

        Raises:
            ValueError: If data format is invalid
        """
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

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "T"

    @property
    def device_class(self) -> str:
        """Home Assistant device class."""
        return ""  # No specific device class for magnetic flux density

    @property
    def state_class(self) -> str:
        """Home Assistant state class."""
        return "measurement"
