"""Local East Coordinate characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint24Template


class LocalEastCoordinateCharacteristic(BaseCharacteristic[float]):
    """Local East Coordinate characteristic (0x2AB1).

    org.bluetooth.characteristic.local_east_coordinate

    Local East Coordinate characteristic.
    """

    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    # SIG spec: sint24 with 0.1 m resolution → fixed 3-byte payload; no GSS YAML
    expected_length = 3
    min_length = 3
    max_length = 3
    _template = ScaledSint24Template(scale_factor=0.1)
