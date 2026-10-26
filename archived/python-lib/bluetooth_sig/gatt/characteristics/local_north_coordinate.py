"""Local North Coordinate characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class LocalNorthCoordinateCharacteristic(BaseCharacteristic[float]):
    """Local North Coordinate characteristic (0x2AB0).

    org.bluetooth.characteristic.local_north_coordinate

    Local North Coordinate characteristic.
    """

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    # IPS v1.0 spec Section 3.4: sint16 in decimeters, 0.1 m/unit → fixed 2-byte payload
    expected_length = 2
    min_length = 2
    max_length = 2
    _template = ScaledSint16Template(scale_factor=0.1)
