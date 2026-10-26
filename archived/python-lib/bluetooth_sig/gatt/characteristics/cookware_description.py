"""Cookware Description characteristic (0x2C25)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class CookwareDescriptionCharacteristic(BaseCharacteristic[str]):
    """Cookware Description characteristic (0x2C25).

    org.bluetooth.characteristic.cookware_description
    """

    _template = Utf8StringTemplate()
