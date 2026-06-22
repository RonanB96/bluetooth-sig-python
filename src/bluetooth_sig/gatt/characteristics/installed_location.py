"""Installed Location characteristic (0x2C34)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class InstalledLocationCharacteristic(BaseCharacteristic[int]):
    """Installed Location characteristic (0x2C34).

    org.bluetooth.characteristic.installed_location

    Bluetooth Assigned Numbers defines this characteristic as a
    one-octet location code.
    """

    _template = Uint8Template()
