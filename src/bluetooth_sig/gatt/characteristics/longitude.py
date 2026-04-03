"""Longitude characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint32Template


class LongitudeCharacteristic(BaseCharacteristic[float]):
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
