"""Device Information Service implementation."""

from dataclasses import dataclass
from typing import Dict, Type

from .base import BaseGattService
from ..characteristics import CharacteristicRegistry
from ..characteristics.device_info import (
    FirmwareRevisionStringCharacteristic,
    HardwareRevisionStringCharacteristic,
    ManufacturerNameStringCharacteristic,
    ModelNumberStringCharacteristic,
    SerialNumberStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
)


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

    def process_characteristics(self, characteristics: Dict[str, Dict]) -> None:
        """Process device information characteristics."""
        for uuid, props in characteristics.items():
            uuid = uuid.replace("-", "").upper()
            char = CharacteristicRegistry.create_characteristic(
                uuid=uuid, properties=set(props.get("properties", []))
            )
            if char:
                self.characteristics[uuid] = char
