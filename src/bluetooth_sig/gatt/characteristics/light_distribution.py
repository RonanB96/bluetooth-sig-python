"""Light Distribution characteristic (0x2BE3)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class LightDistributionType(IntEnum):
    """Light distribution type values.

    Values:
        NOT_SPECIFIED: Type not specified (0x00)
        TYPE_I: Type I distribution (0x01)
        TYPE_II: Type II distribution (0x02)
        TYPE_III: Type III distribution (0x03)
        TYPE_IV: Type IV distribution (0x04)
        TYPE_V: Type V distribution (0x05)
    """

    NOT_SPECIFIED = 0x00
    TYPE_I = 0x01
    TYPE_II = 0x02
    TYPE_III = 0x03
    TYPE_IV = 0x04
    TYPE_V = 0x05


class LightDistributionCharacteristic(BaseCharacteristic[LightDistributionType]):
    """Light Distribution characteristic (0x2BE3).

    org.bluetooth.characteristic.light_distribution

    Type of light distribution pattern.
    """

    _template = EnumTemplate.uint8(LightDistributionType)
