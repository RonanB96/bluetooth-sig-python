"""Registry of supported GATT characteristics."""

from typing import Dict, Optional, Type

from ..uuid_registry import uuid_registry
from .base import BaseCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .device_info import (
    FirmwareRevisionStringCharacteristic,
    HardwareRevisionStringCharacteristic,
    ManufacturerNameStringCharacteristic,
    ModelNumberStringCharacteristic,
    SerialNumberStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
)
from .generic_access import AppearanceCharacteristic, DeviceNameCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .humidity import HumidityCharacteristic
from .illuminance import IlluminanceCharacteristic
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .sound_pressure_level import SoundPressureLevelCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .uv_index import UVIndexCharacteristic


class CharacteristicRegistry:
    """Registry for all supported GATT characteristics."""

    _characteristics: Dict[str, Type[BaseCharacteristic]] = {
        "Battery Level": BatteryLevelCharacteristic,
        "Temperature": TemperatureCharacteristic,
        "Temperature Measurement": TemperatureMeasurementCharacteristic,
        "Humidity": HumidityCharacteristic,
        "Pressure": PressureCharacteristic,
        "UV Index": UVIndexCharacteristic,
        "Illuminance": IlluminanceCharacteristic,
        "Power Specification": SoundPressureLevelCharacteristic,
        "Heart Rate Measurement": HeartRateMeasurementCharacteristic,
        "Blood Pressure Measurement": BloodPressureMeasurementCharacteristic,
        "PLX Continuous Measurement": PulseOximetryMeasurementCharacteristic,
        "CSC Measurement": CSCMeasurementCharacteristic,
        "RSC Measurement": RSCMeasurementCharacteristic,
        "Manufacturer Name String": ManufacturerNameStringCharacteristic,
        "Model Number String": ModelNumberStringCharacteristic,
        "Serial Number String": SerialNumberStringCharacteristic,
        "Firmware Revision String": FirmwareRevisionStringCharacteristic,
        "Hardware Revision String": HardwareRevisionStringCharacteristic,
        "Software Revision String": SoftwareRevisionStringCharacteristic,
        "Device Name": DeviceNameCharacteristic,
        "Appearance": AppearanceCharacteristic,
    }

    @classmethod
    def get_characteristic_class(cls, name: str) -> Optional[Type[BaseCharacteristic]]:
        """Get the characteristic class for a given name."""
        return cls._characteristics.get(name)

    @classmethod
    def get_characteristic_class_by_uuid(
        cls, uuid: str
    ) -> Optional[Type[BaseCharacteristic]]:
        """Get the characteristic class for a given UUID by looking up in registry."""
        # Normalize the UUID
        uuid = uuid.replace("-", "").upper()

        # Extract UUID16 from full UUID pattern
        if len(uuid) == 32:  # Full UUID without dashes
            uuid16 = uuid[4:8]
        elif len(uuid) == 4:  # Already a short UUID
            uuid16 = uuid
        else:
            return None

        # Find the characteristic name by UUID
        char_info = uuid_registry.get_characteristic_info(uuid16)
        if char_info:
            return cls._characteristics.get(char_info.name)

        return None

    @classmethod
    def create_characteristic(cls, uuid: str, **kwargs) -> Optional[BaseCharacteristic]:
        """Create a characteristic instance for the given UUID."""
        char_class = cls.get_characteristic_class_by_uuid(uuid)
        if not char_class:
            return None

        return char_class(uuid=uuid, **kwargs)
