"""Latitude characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint32Template


class LatitudeCharacteristic(BaseCharacteristic[float]):
    """Latitude characteristic (0x2AAE).

    org.bluetooth.characteristic.latitude

    Latitude characteristic representing geographic coordinate in degrees.
    Encoded as sint32 with scale factor 1e-7 degrees per unit.
    """

    _python_type: type | str | None = float

    # Geographic coordinate constants
    DEGREE_SCALING_FACTOR = 1e-7  # 10^-7 degrees per unit

    # SIG range not encoded in YAML; enforce spec bounds [-90, 90] degrees.
    min_value = -90.0
    max_value = 90.0
    expected_type = float

    _template = ScaledSint32Template(scale_factor=DEGREE_SCALING_FACTOR)
