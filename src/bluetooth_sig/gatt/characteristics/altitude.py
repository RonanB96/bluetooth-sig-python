"""Altitude characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class AltitudeCharacteristic(BaseCharacteristic[float]):
    """Altitude characteristic (0x2AB3).

    org.bluetooth.characteristic.altitude

    Altitude characteristic.
    """

    # Validation attributes
    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    # SIG spec: sint16, resolution 0.1 m → fixed 2-byte payload
    # No GSS YAML available, so set explicit length from spec
    expected_length = 2
    min_length = 2
    max_length = 2
    _template = ScaledSint16Template(scale_factor=0.1)
