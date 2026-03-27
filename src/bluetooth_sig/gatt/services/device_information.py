"""Device Information Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class DeviceInformationService(BaseGattService):
    """Device Information Service implementation.

    Contains characteristics that expose device information:
    - Manufacturer Name String - Required
    - Model Number String - Optional
    - Serial Number String - Optional
    - Hardware Revision String - Optional
    - Firmware Revision String - Optional
    - Software Revision String - Optional
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.MANUFACTURER_NAME_STRING: True,
        CharacteristicName.MODEL_NUMBER_STRING: False,
        CharacteristicName.SERIAL_NUMBER_STRING: False,
        CharacteristicName.HARDWARE_REVISION_STRING: False,
        CharacteristicName.FIRMWARE_REVISION_STRING: False,
        CharacteristicName.SOFTWARE_REVISION_STRING: False,
    }
