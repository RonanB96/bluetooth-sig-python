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
        "float"  # Override YAML int type since decode_value returns float
    )

    def decode_value(self, data: bytearray) -> float:
        """Parse magnetic declination data (uint16 in units of 0.01 degrees)."""
        if len(data) < 2:
            raise ValueError("Magnetic declination data must be at least 2 bytes")

        # Convert uint16 (little endian) to degrees
        declination_raw = int.from_bytes(data[:2], byteorder="little", signed=False)
        return declination_raw * 0.01

    def encode_value(self, data: float | int) -> bytearray:
        """Encode magnetic declination value back to bytes.

        Args:
            data: Magnetic declination in degrees

        Returns:
            Encoded bytes representing the magnetic declination (uint16, 0.01 degrees resolution)
        """
        declination = float(data)

        # Normalize to 0-360 range if needed (magnetic declination can be 0-360)
        declination = declination % 360.0

        # Validate range (0 to 359.99 degrees)
        if not 0.0 <= declination < 360.0:
            raise ValueError(
                f"Magnetic declination {declination}° is outside valid range (0.0 to 359.99°)"
            )

        # Convert degrees to raw value (multiply by 100 for 0.01 degree resolution)
        declination_raw = round(declination * 100)

        # Ensure it fits in uint16
        if declination_raw > 65535:  # pylint: disable=consider-using-min-builtin # Clear intent for range clamping
            declination_raw = 65535

        return bytearray(declination_raw.to_bytes(2, byteorder="little", signed=False))

    @property
    def unit(self) -> str:
        """Get the unit of measurement."""
        return "°"
