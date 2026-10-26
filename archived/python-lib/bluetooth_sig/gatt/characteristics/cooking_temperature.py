"""Cooking Temperature characteristic (0x2C2E)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint16Template


class CookingTemperatureCharacteristic(BaseCharacteristic[float]):
    """Cooking Temperature characteristic (0x2C2E).

    org.bluetooth.characteristic.cooking_temperature
    """

    _template = ScaledSint16Template.from_letter_method(M=1, d=-1, b=0)
