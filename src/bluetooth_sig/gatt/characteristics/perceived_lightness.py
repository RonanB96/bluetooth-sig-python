"""Perceived Lightness characteristic (0x2B03)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint16Template


class PerceivedLightnessCharacteristic(BaseCharacteristic[int]):
    """Perceived Lightness characteristic (0x2B03).

    org.bluetooth.characteristic.perceived_lightness

    Unitless perceived lightness value (0-65535).
    """

    _template = Uint16Template()
