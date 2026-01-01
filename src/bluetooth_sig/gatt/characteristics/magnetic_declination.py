"""Magnetic Declination characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import ValueType
from ...types.units import AngleUnit
from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class MagneticDeclinationCharacteristic(BaseCharacteristic):
    """Magnetic Declination characteristic (0x2A2C).

    org.bluetooth.characteristic.magnetic_declination

    Magnetic declination characteristic.

    Represents the magnetic declination - the angle on the horizontal plane
    between the direction of True North (geographic) and the direction of
    Magnetic North, measured clockwise from True North to Magnetic North.
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-2, b=0)

    _characteristic_name: str = "Magnetic Declination"
    # Override YAML int type since decode_value returns float
    _manual_value_type: ValueType | str | None = ValueType.FLOAT
    _manual_unit: str = AngleUnit.DEGREES.value  # Override template's "units" default

    # Template configuration
    resolution: float = 0.01  # 0.01 degree resolution

    expected_type: type = float

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
