"""True Wind Speed characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class TrueWindSpeedCharacteristic(BaseCharacteristic):
    """True Wind Speed measurement characteristic."""

    _template = ScaledUint16Template()

    _characteristic_name: str = "True Wind Speed"
