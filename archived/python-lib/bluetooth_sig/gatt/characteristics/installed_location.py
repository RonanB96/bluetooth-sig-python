"""Installed Location characteristic (0x2C34)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class InstalledLocationCharacteristic(BaseCharacteristic[str]):
    """Installed Location characteristic (0x2C34).

    org.bluetooth.characteristic.installed_location

    VAS defines this characteristic as a variable-length UTF-8 string.
    """

    _template = Utf8StringTemplate()
