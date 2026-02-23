"""Location Name characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class LocationNameCharacteristic(BaseCharacteristic[str]):
    """Location Name characteristic (0x2AB5).

    org.bluetooth.characteristic.location_name

    Location Name characteristic.
    """

    _python_type: type | str | None = str

    _template = Utf8StringTemplate()
    min_length = 0
