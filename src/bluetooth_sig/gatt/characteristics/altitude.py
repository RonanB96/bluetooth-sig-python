"""Altitude characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class AltitudeCharacteristic(BaseCharacteristic):
    """Altitude characteristic (0x2AB3).

    org.bluetooth.characteristic.altitude

    Altitude characteristic.
    """

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    _manual_value_type = "float"
    _template = ScaledSint16Template(scale_factor=0.1)
