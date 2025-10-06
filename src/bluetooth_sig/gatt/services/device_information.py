"""Device Information Service implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


@dataclass
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
        CharacteristicName.MANUFACTURER_NAME_STRING: True,  # required
        CharacteristicName.MODEL_NUMBER_STRING: False,  # optional
        CharacteristicName.SERIAL_NUMBER_STRING: False,  # optional
        CharacteristicName.HARDWARE_REVISION_STRING: False,  # optional
        CharacteristicName.FIRMWARE_REVISION_STRING: False,  # optional
        CharacteristicName.SOFTWARE_REVISION_STRING: False,  # optional
    }
