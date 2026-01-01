"""Longitude characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint32Template


class LongitudeCharacteristic(BaseCharacteristic):
    """Longitude characteristic (0x2AAF).

    org.bluetooth.characteristic.longitude

    Longitude characteristic representing geographic coordinate in degrees.
    Encoded as sint32 with scale factor 1e-7 degrees per unit.
    """

    # Geographic coordinate constants
    DEGREE_SCALING_FACTOR = 1e-7  # 10^-7 degrees per unit

    # SIG range not encoded in YAML; enforce spec bounds [-180, 180] degrees.
    min_value = -180.0
    max_value = 180.0
    expected_type = float

    _template = ScaledSint32Template(scale_factor=DEGREE_SCALING_FACTOR)

    def encode_value(self, data: float) -> bytearray:
        """Encode longitude with range validation.

        Args:
            data: Longitude value in degrees (-180 to +180)

        Returns:
            Encoded characteristic data (4 bytes)

        Raises:
            ValueError: If longitude is outside valid range [-180, 180]
        """
        if not self.min_value <= data <= self.max_value:
            raise ValueError(f"Longitude {data} out of range [{self.min_value}, {self.max_value}]")
        return self._template.encode_value(data)
