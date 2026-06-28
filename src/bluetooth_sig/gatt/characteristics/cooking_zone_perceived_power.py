"""Cooking Zone Perceived Power characteristic (0x2C2F)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class CookingZonePerceivedPowerCharacteristic(BaseCharacteristic[float]):
    """Cooking Zone Perceived Power characteristic (0x2C2F).

    org.bluetooth.characteristic.cooking_zone_perceived_power
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-1, b=0)
