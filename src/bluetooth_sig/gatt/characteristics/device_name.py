"""Device Name characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class DeviceNameCharacteristic(BaseCharacteristic):
    """Device Name characteristic (0x2A00).

    org.bluetooth.characteristic.gap.device_name

    Represents the device name as a UTF-8 string.
    """

    _template = Utf8StringTemplate()
