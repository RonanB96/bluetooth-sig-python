"""Local East Coordinate characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint24Template


class LocalEastCoordinateCharacteristic(BaseCharacteristic):
    """Local East Coordinate characteristic (0x2AB1).

    org.bluetooth.characteristic.local_east_coordinate

    Local East Coordinate characteristic.
    """

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    _manual_value_type = "float"
    _template = ScaledSint24Template(scale_factor=0.1)

    expected_length: int = 3
    expected_type: type = float
