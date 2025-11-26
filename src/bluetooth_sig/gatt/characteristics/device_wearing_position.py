"""Device Wearing Position characteristic (0x2B4B)."""

from .base import BaseCharacteristic
from .templates import Uint8Template


class DeviceWearingPositionCharacteristic(BaseCharacteristic):
    """Device Wearing Position characteristic (0x2B4B).

    org.bluetooth.characteristic.device_wearing_position

    Device Wearing Position characteristic.
    """

    _template = Uint8Template()
