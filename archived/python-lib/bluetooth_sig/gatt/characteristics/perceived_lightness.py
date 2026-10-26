"""Perceived Lightness characteristic (0x2B03)."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint16Template


class PerceivedLightnessCharacteristic(BaseCharacteristic[int]):
    """Perceived Lightness characteristic (0x2B03).

    org.bluetooth.characteristic.perceived_lightness

    Unitless perceived lightness value (0-65535).
    """

    _manual_role = CharacteristicRole.MEASUREMENT
    _template = Uint16Template()
