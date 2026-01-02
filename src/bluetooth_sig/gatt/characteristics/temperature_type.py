"""Temperature Type characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class TemperatureType(IntEnum):
    """Temperature measurement location enumeration.

    Values correspond to IEEE 11073-10408-2008 Temperature Type descriptions.
    """

    RESERVED_0 = 0  # Reserved for Future Use
    ARMPIT = 1
    BODY_GENERAL = 2
    EAR = 3  # Usually earlobe
    FINGER = 4
    GASTROINTESTINAL_TRACT = 5
    MOUTH = 6
    RECTUM = 7
    TOE = 8
    TYMPANUM = 9  # Ear drum


class TemperatureTypeCharacteristic(BaseCharacteristic):
    """Temperature Type characteristic (0x2A1D).

    org.bluetooth.characteristic.temperature_type

    Indicates the location of the temperature measurement as an 8-bit enumeration.
    """

    _template = EnumTemplate.uint8(TemperatureType)
