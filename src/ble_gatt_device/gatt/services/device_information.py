"""Device Information Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from ..characteristics.device_info import (
    FirmwareRevisionStringCharacteristic,
    HardwareRevisionStringCharacteristic,
    ManufacturerNameStringCharacteristic,
    ModelNumberStringCharacteristic,
    SerialNumberStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
)
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

    @classmethod
    def get_expected_characteristics(cls) -> Dict[str, Type]:
        """Get the expected characteristics for this service by name and class."""
        return {
            "Manufacturer Name String": ManufacturerNameStringCharacteristic,
            "Model Number String": ModelNumberStringCharacteristic,
            "Serial Number String": SerialNumberStringCharacteristic,
            "Hardware Revision String": HardwareRevisionStringCharacteristic,
            "Firmware Revision String": FirmwareRevisionStringCharacteristic,
            "Software Revision String": SoftwareRevisionStringCharacteristic,
        }

    @classmethod
    def get_required_characteristics(cls) -> Dict[str, Type]:
        """Get the required characteristics for this service by name and class."""
        return {
            "Manufacturer Name String": ManufacturerNameStringCharacteristic,
        }
