"""Advertising Constant Tone Extension PHY characteristic (0x2BB2)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class CTEPHY(IntEnum):
    """Constant Tone Extension PHY type."""

    LE_1M = 1
    LE_2M = 2
    LE_CODED = 3


class AdvertisingConstantToneExtensionPhyCharacteristic(BaseCharacteristic[CTEPHY]):
    """Advertising Constant Tone Extension PHY characteristic (0x2BB2).

    org.bluetooth.characteristic.advertising_constant_tone_extension_phy

    The PHY used for Constant Tone Extension advertising.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(CTEPHY)
