"""Device Wearing Position characteristic (0x2B4B)."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from .base import BaseCharacteristic
from .templates import Uint8Template


class DeviceWearingPositionCharacteristic(BaseCharacteristic[int]):
    """Device Wearing Position characteristic (0x2B4B).

    org.bluetooth.characteristic.device_wearing_position

    Device Wearing Position characteristic.
    """

    _manual_role = CharacteristicRole.STATUS
    _template = Uint8Template()
