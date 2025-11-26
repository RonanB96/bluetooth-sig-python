"""VO2 Max characteristic (0x2A96)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class VO2MaxCharacteristic(BaseCharacteristic):
    """VO2 Max characteristic (0x2A96).

    org.bluetooth.characteristic.vo2_max

    VO2 Max characteristic.
    """

    _template = Uint8Template()  # ml/kg/min
