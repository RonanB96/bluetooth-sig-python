"""Local North Coordinate characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint24Template


class LocalNorthCoordinateCharacteristic(BaseCharacteristic):
    """Local North Coordinate characteristic (0x2AB0).

    org.bluetooth.characteristic.local_north_coordinate

    Local North Coordinate characteristic.
    """

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    _manual_value_type = "float"
    _template = ScaledSint24Template(scale_factor=0.1)

    expected_length: int = 3
    expected_type: type = float
