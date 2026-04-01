"""Altitude characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class AltitudeCharacteristic(BaseCharacteristic[float]):
    """Altitude characteristic (0x2AB3).

    org.bluetooth.characteristic.altitude

    Altitude above the WGS84 ellipsoid.
    """

    # Validation attributes
    # Manual overrides required as Bluetooth SIG registry doesn't provide unit/value type
    _manual_unit = "m"
    # IPS spec §3.7: uint16; x = h_dm + 1000 where h_dm is altitude in decimetres.
    # Decoded value (metres) = (x − 1000) × 0.1 → scale_factor=0.1, offset=−1000.
    # 0xFFFF (65535) means "not configured".
    expected_length = 2
    min_length = 2
    max_length = 2
    _template = ScaledUint16Template(scale_factor=0.1, offset=-1000)
