"""Bearer Technology characteristic (0x2BB5)."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class BearerTechnology(IntEnum):
    """Bearer technology type."""

    THREEG = 0x01
    FOURGEE = 0x02
    LTE = 0x03
    WIFI = 0x04
    FIVEG = 0x05
    GSM = 0x06
    CDMA = 0x07
    TWOG = 0x08
    WCDMA = 0x09


class BearerTechnologyCharacteristic(BaseCharacteristic[BearerTechnology]):
    """Bearer Technology characteristic (0x2BB5).

    org.bluetooth.characteristic.bearer_technology

    Technology used by the telephone bearer.
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(BearerTechnology)
