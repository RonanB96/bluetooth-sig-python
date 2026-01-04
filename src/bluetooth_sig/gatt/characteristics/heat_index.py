"""Heat Index characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class HeatIndexCharacteristic(BaseCharacteristic[int]):
    """Heat Index characteristic (0x2A7A).

    org.bluetooth.characteristic.heat_index

    Heat Index measurement characteristic.
    """

    _template = Uint8Template()
