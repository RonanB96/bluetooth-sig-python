"""Content Control ID characteristic (0x2BBA)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class ContentControlIdCharacteristic(BaseCharacteristic[int]):
    """Content Control ID characteristic (0x2BBA).

    org.bluetooth.characteristic.content_control_id

    The ID of the content control service instance.
    """

    _template = Uint8Template()
