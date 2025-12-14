"""Device Wearing Position characteristic (0x2B4B)."""

from __future__ import annotations

from ..constants import UINT8_MAX
from .base import BaseCharacteristic
from .templates import Uint8Template


class DeviceWearingPositionCharacteristic(BaseCharacteristic):
    """Device Wearing Position characteristic (0x2B4B).

    org.bluetooth.characteristic.device_wearing_position

    Device Wearing Position characteristic.
    """

    # Validation attributes
    expected_length: int = 1  # uint8
    min_value: int = 0
    max_value: int = UINT8_MAX
    expected_type: type = int

    _template = Uint8Template()
