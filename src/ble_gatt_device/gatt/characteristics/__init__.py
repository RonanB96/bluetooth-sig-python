"""Registry of supported GATT characteristics."""

from typing import Dict, Optional, Type

from ..uuid_registry import uuid_registry
from .ammonia_concentration import AmmoniaConcentrationCharacteristic
from .apparent_wind_direction import ApparentWindDirectionCharacteristic
from .apparent_wind_speed import ApparentWindSpeedCharacteristic
from .average_current import AverageCurrentCharacteristic
from .average_voltage import AverageVoltageCharacteristic
from .barometric_pressure_trend import BarometricPressureTrendCharacteristic
from .base import BaseCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .battery_power_state import BatteryPowerStateCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic
from .body_composition_measurement import BodyCompositionMeasurementCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
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
from .dew_point import DewPointCharacteristic
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .elevation import ElevationCharacteristic
from .generic_access import AppearanceCharacteristic, DeviceNameCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic
from .glucose_measurement import GlucoseMeasurementCharacteristic
from .glucose_measurement_context import GlucoseMeasurementContextCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .heat_index import HeatIndexCharacteristic
from .high_voltage import HighVoltageCharacteristic
from .humidity import HumidityCharacteristic
from .illuminance import IlluminanceCharacteristic
from .local_time_information import LocalTimeInformationCharacteristic
from .magnetic_declination import MagneticDeclinationCharacteristic
from .magnetic_flux_density_2d import MagneticFluxDensity2DCharacteristic
from .magnetic_flux_density_3d import MagneticFluxDensity3DCharacteristic
from .methane_concentration import MethaneConcentrationCharacteristic
from .nitrogen_dioxide_concentration import NitrogenDioxideConcentrationCharacteristic
from .ozone_concentration import OzoneConcentrationCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pollen_concentration import PollenConcentrationCharacteristic
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rainfall import RainfallCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .sound_pressure_level import SoundPressureLevelCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .time_zone import TimeZoneCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .tvoc_concentration import TVOCConcentrationCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .uv_index import UVIndexCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .weight_measurement import WeightMeasurementCharacteristic
from .weight_scale_feature import WeightScaleFeatureCharacteristic
from .wind_chill import WindChillCharacteristic


class CharacteristicRegistry:
    """Registry for all supported GATT characteristics."""

    _characteristics: Dict[str, Type[BaseCharacteristic]] = {
        "Battery Level": BatteryLevelCharacteristic,
        "Battery Level Status": BatteryPowerStateCharacteristic,
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
        "Glucose Measurement": GlucoseMeasurementCharacteristic,
        "Glucose Measurement Context": GlucoseMeasurementContextCharacteristic,
        "Glucose Feature": GlucoseFeatureCharacteristic,
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
        # Navigation and positioning characteristics
        "Magnetic Declination": MagneticDeclinationCharacteristic,
        "Magnetic Flux Density - 2D": MagneticFluxDensity2DCharacteristic,
        "Magnetic Flux Density - 3D": MagneticFluxDensity3DCharacteristic,
        "Elevation": ElevationCharacteristic,
        "Barometric Pressure Trend": BarometricPressureTrendCharacteristic,
        # Time-related characteristics
        "Time Zone": TimeZoneCharacteristic,
        "Local Time Information": LocalTimeInformationCharacteristic,
        # Environmental sensors
        "Pollen Concentration": PollenConcentrationCharacteristic,
        "Rainfall": RainfallCharacteristic,
        # Gas sensor characteristics for air quality monitoring
        "CO\\textsubscript{2} Concentration": CO2ConcentrationCharacteristic,
        "VOC Concentration": TVOCConcentrationCharacteristic,
        "Ammonia Concentration": AmmoniaConcentrationCharacteristic,
        "Methane Concentration": MethaneConcentrationCharacteristic,
        "Nitrogen Dioxide Concentration": NitrogenDioxideConcentrationCharacteristic,
        "Ozone Concentration": OzoneConcentrationCharacteristic,
        "Particulate Matter - PM1 Concentration": PM1ConcentrationCharacteristic,
        "Particulate Matter - PM2.5 Concentration": PM25ConcentrationCharacteristic,
        "Particulate Matter - PM10 Concentration": PM10ConcentrationCharacteristic,
        "Sulfur Dioxide Concentration": SulfurDioxideConcentrationCharacteristic,
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
