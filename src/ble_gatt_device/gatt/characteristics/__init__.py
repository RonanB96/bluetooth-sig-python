"""Registry of supported GATT characteristics."""

from typing import Dict, Optional, Type

from ..uuid_registry import uuid_registry
from .average_current import AverageCurrentCharacteristic
from .average_voltage import AverageVoltageCharacteristic
from .base import BaseCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic
from .body_composition_measurement import BodyCompositionMeasurementCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .cycling_power_control_point import CyclingPowerControlPointCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .cycling_power_measurement import CyclingPowerMeasurementCharacteristic
from .cycling_power_vector import CyclingPowerVectorCharacteristic
from .device_info import (
    FirmwareRevisionStringCharacteristic,
    HardwareRevisionStringCharacteristic,
    ManufacturerNameStringCharacteristic,
    ModelNumberStringCharacteristic,
    SerialNumberStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
)
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .generic_access import AppearanceCharacteristic, DeviceNameCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .high_voltage import HighVoltageCharacteristic
from .humidity import HumidityCharacteristic
from .illuminance import IlluminanceCharacteristic
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .sound_pressure_level import SoundPressureLevelCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .uv_index import UVIndexCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .weight_measurement import WeightMeasurementCharacteristic
from .weight_scale_feature import WeightScaleFeatureCharacteristic
from .dew_point import DewPointCharacteristic
from .heat_index import HeatIndexCharacteristic
from .wind_chill import WindChillCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .apparent_wind_speed import ApparentWindSpeedCharacteristic
from .apparent_wind_direction import ApparentWindDirectionCharacteristic


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
        "Cycling Power Measurement": CyclingPowerMeasurementCharacteristic,
        "Cycling Power Feature": CyclingPowerFeatureCharacteristic,
        "Cycling Power Vector": CyclingPowerVectorCharacteristic,
        "Cycling Power Control Point": CyclingPowerControlPointCharacteristic,
        "Manufacturer Name String": ManufacturerNameStringCharacteristic,
        "Model Number String": ModelNumberStringCharacteristic,
        "Serial Number String": SerialNumberStringCharacteristic,
        "Firmware Revision String": FirmwareRevisionStringCharacteristic,
        "Hardware Revision String": HardwareRevisionStringCharacteristic,
        "Software Revision String": SoftwareRevisionStringCharacteristic,
        "Device Name": DeviceNameCharacteristic,
        "Appearance": AppearanceCharacteristic,
        "Weight Measurement": WeightMeasurementCharacteristic,
        "Weight Scale Feature": WeightScaleFeatureCharacteristic,
        "Body Composition Measurement": BodyCompositionMeasurementCharacteristic,
        "Body Composition Feature": BodyCompositionFeatureCharacteristic,
        # Electrical Power Monitoring Characteristics
        "Electric Current": ElectricCurrentCharacteristic,
        "Voltage": VoltageCharacteristic,
        "Average Current": AverageCurrentCharacteristic,
        "Average Voltage": AverageVoltageCharacteristic,
        "Electric Current Range": ElectricCurrentRangeCharacteristic,
        "Electric Current Specification": ElectricCurrentSpecificationCharacteristic,
        "Electric Current Statistics": ElectricCurrentStatisticsCharacteristic,
        "Voltage Specification": VoltageSpecificationCharacteristic,
        "Voltage Statistics": VoltageStatisticsCharacteristic,
        "High Voltage": HighVoltageCharacteristic,
        "Voltage Frequency": VoltageFrequencyCharacteristic,
        "Supported Power Range": SupportedPowerRangeCharacteristic,
        "Tx Power Level": TxPowerLevelCharacteristic,
        # Environmental Sensing Characteristics
        "Dew Point": DewPointCharacteristic,
        "Heat Index": HeatIndexCharacteristic,
        "Wind Chill": WindChillCharacteristic,
        "True Wind Speed": TrueWindSpeedCharacteristic,
        "True Wind Direction": TrueWindDirectionCharacteristic,
        "Apparent Wind Speed": ApparentWindSpeedCharacteristic,
        "Apparent Wind Direction": ApparentWindDirectionCharacteristic,
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
