"""Model Number String characteristic (0x2A24)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class ModelNumberStringCharacteristic(BaseCharacteristic[str]):
    """Model Number String characteristic (0x2A24).

    org.bluetooth.characteristic.model_number_string

    Model Number String characteristic.
    """

    _template = Utf8StringTemplate()
