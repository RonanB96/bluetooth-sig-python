"""Location Name characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class LocationNameCharacteristic(BaseCharacteristic):
    """Location Name characteristic (0x2AB5).

    org.bluetooth.characteristic.location_name

    Location Name characteristic.
    """

    _template = Utf8StringTemplate()
