"""Altitude characteristic implementation."""

from __future__ import annotations

from ..constants import SINT16_MAX, SINT16_MIN
from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class AltitudeCharacteristic(BaseCharacteristic):
    """Altitude characteristic (0x2AB3).

    org.bluetooth.characteristic.altitude

    Altitude characteristic.
    """

    # Validation attributes
    expected_length: int = 2  # sint16
    min_value: float = SINT16_MIN * 0.1  # Min scaled value
    max_value: float = SINT16_MAX * 0.1  # Max scaled value
    expected_type: type = float

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    _manual_value_type = "float"
    _template = ScaledSint16Template(scale_factor=0.1)
