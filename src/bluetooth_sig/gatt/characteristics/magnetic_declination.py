"""Magnetic Declination characteristic implementation."""

from dataclasses import dataclass

from .templates import ScaledUint16Characteristic


@dataclass
class MagneticDeclinationCharacteristic(ScaledUint16Characteristic):
    """Magnetic declination characteristic.

    Represents the magnetic declination - the angle on the horizontal plane
    between the direction of True North (geographic) and the direction of
    Magnetic North, measured clockwise from True North to Magnetic North.
    """

    _characteristic_name: str = "Magnetic Declination"
    _manual_value_type: str = "float"  # Override YAML int type since decode_value returns float

    # Template configuration
    resolution: float = 0.01  # 0.01 degree resolution
    measurement_unit: str = "°"
    max_value: float = 655.35  # 65535 * 0.01 degrees max

    def encode_value(self, data: float) -> bytearray:
        """Encode magnetic declination value back to bytes.

        Args:
            data: Magnetic declination in degrees

        Returns:
            Encoded bytes representing the magnetic declination (uint16, 0.01 degrees resolution)
        """
        declination = float(data)

        # Normalize to 0-360 range if needed (magnetic declination can be 0-360)
        declination = declination % 360.0

        # Use template encoding after normalization
        return super().encode_value(declination)
