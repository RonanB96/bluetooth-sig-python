"""Manufacturer Name String characteristic (0x2A29)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class ManufacturerNameStringCharacteristic(BaseCharacteristic):
    """Manufacturer Name String characteristic (0x2A29).

    org.bluetooth.characteristic.manufacturer_name_string

    Manufacturer Name String characteristic.
    """

    _template = Utf8StringTemplate()
    min_length = 0
