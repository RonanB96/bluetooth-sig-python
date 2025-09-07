"""Magnetic Declination characteristic implementation."""

from dataclasses import dataclass

from .base import BaseCharacteristic


@dataclass
class MagneticDeclinationCharacteristic(BaseCharacteristic):
    """Magnetic declination characteristic.

    Represents the magnetic declination - the angle on the horizontal plane
    between the direction of True North (geographic) and the direction of
    Magnetic North, measured clockwise from True North to Magnetic North.
    """

    _characteristic_name: str = "Magnetic Declination"
    _manual_value_type: str = (
        "float"  # Override YAML int type since parse_value returns float
    )

    def parse_value(self, data: bytearray) -> float:
        """Parse magnetic declination data (uint16 in units of 0.01 degrees)."""
        if len(data) < 2:
            raise ValueError("Magnetic declination data must be at least 2 bytes")

        # Convert uint16 (little endian) to degrees
        declination_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return declination_raw * 0.01

    def encode_value(self, data) -> bytearray:
        """Encode value back to bytes - basic stub implementation."""
        # TODO: Implement proper encoding
        raise NotImplementedError(
            "encode_value not yet implemented for this characteristic"
        )

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°"
