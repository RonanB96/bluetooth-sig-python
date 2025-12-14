"""Wind Chill characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledSint8Template


class WindChillCharacteristic(BaseCharacteristic):
    """Wind Chill characteristic (0x2A79).

    org.bluetooth.characteristic.wind_chill

    Wind Chill measurement characteristic.
    """

    _template = ScaledSint8Template.from_letter_method(M=1, d=0, b=0)

    expected_length: int = 1
    expected_type: type = int
