"""Bluetooth SIG GATT characteristic registry.
Provides type-safe, registry-driven lookup for all supported characteristics.
Now encapsulated in CharacteristicRegistry class for API clarity and extensibility.
"""

# Import the registry components from the dedicated registry module
# Import all individual characteristic classes for backward compatibility
from .ammonia_concentration import AmmoniaConcentrationCharacteristic
from .apparent_wind_direction import ApparentWindDirectionCharacteristic
from .apparent_wind_speed import ApparentWindSpeedCharacteristic
from .average_current import AverageCurrentCharacteristic
from .average_voltage import AverageVoltageCharacteristic
from .barometric_pressure_trend import BarometricPressureTrendCharacteristic
from .base import BaseCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .battery_power_state import BatteryPowerStateCharacteristic
from .blood_pressure_feature import BloodPressureFeatureCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic
from .body_composition_measurement import BodyCompositionMeasurementCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .cycling_power_control_point import CyclingPowerControlPointCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .cycling_power_measurement import CyclingPowerMeasurementCharacteristic
from .cycling_power_vector import CyclingPowerVectorCharacteristic

# Device info classes imported individually below
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
from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
from .ozone_concentration import OzoneConcentrationCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pollen_concentration import PollenConcentrationCharacteristic
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rainfall import RainfallCharacteristic
from .registry import (
    CHARACTERISTIC_CLASS_MAP,
    CHARACTERISTIC_CLASS_MAP_STR,
    CharacteristicName,
    CharacteristicRegistry,
)
from .rsc_measurement import RSCMeasurementCharacteristic
from .sound_pressure_level import SoundPressureLevelCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .time_zone import TimeZoneCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .uv_index import UVIndexCharacteristic
from .voc_concentration import VOCConcentrationCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .weight_measurement import WeightMeasurementCharacteristic
from .weight_scale_feature import WeightScaleFeatureCharacteristic
from .wind_chill import WindChillCharacteristic

__all__ = [
    # Registry components
    "CharacteristicName",
    "CharacteristicRegistry",
    "CHARACTERISTIC_CLASS_MAP",
    "CHARACTERISTIC_CLASS_MAP_STR",
    # Base characteristic
    "BaseCharacteristic",
    # Individual characteristic classes (for backward compatibility)
    "AmmoniaConcentrationCharacteristic",
    "ApparentWindDirectionCharacteristic",
    "ApparentWindSpeedCharacteristic",
    "AverageCurrentCharacteristic",
    "AverageVoltageCharacteristic",
    "BarometricPressureTrendCharacteristic",
    "BatteryLevelCharacteristic",
    "BatteryPowerStateCharacteristic",
    "BloodPressureFeatureCharacteristic",
    "BloodPressureMeasurementCharacteristic",
    "BodyCompositionFeatureCharacteristic",
    "BodyCompositionMeasurementCharacteristic",
    "CO2ConcentrationCharacteristic",
    "CSCMeasurementCharacteristic",
    "CyclingPowerControlPointCharacteristic",
    "CyclingPowerFeatureCharacteristic",
    "CyclingPowerMeasurementCharacteristic",
    "CyclingPowerVectorCharacteristic",
    "AppearanceCharacteristic",
    "DeviceNameCharacteristic",
    "DewPointCharacteristic",
    "ElectricCurrentCharacteristic",
    "ElectricCurrentRangeCharacteristic",
    "ElectricCurrentSpecificationCharacteristic",
    "ElectricCurrentStatisticsCharacteristic",
    "ElevationCharacteristic",
    "FirmwareRevisionStringCharacteristic",
    "GlucoseFeatureCharacteristic",
    "GlucoseMeasurementCharacteristic",
    "GlucoseMeasurementContextCharacteristic",
    "HeartRateMeasurementCharacteristic",
    "HeatIndexCharacteristic",
    "HighVoltageCharacteristic",
    "HumidityCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "IlluminanceCharacteristic",
    "LocalTimeInformationCharacteristic",
    "MagneticDeclinationCharacteristic",
    "MagneticFluxDensity2DCharacteristic",
    "MagneticFluxDensity3DCharacteristic",
    "ManufacturerNameStringCharacteristic",
    "MethaneConcentrationCharacteristic",
    "ModelNumberStringCharacteristic",
    "NitrogenDioxideConcentrationCharacteristic",
    "NonMethaneVOCConcentrationCharacteristic",
    "OzoneConcentrationCharacteristic",
    "PM1ConcentrationCharacteristic",
    "PM10ConcentrationCharacteristic",
    "PM25ConcentrationCharacteristic",
    "PollenConcentrationCharacteristic",
    "PressureCharacteristic",
    "PulseOximetryMeasurementCharacteristic",
    "RainfallCharacteristic",
    "RSCMeasurementCharacteristic",
    "SerialNumberStringCharacteristic",
    "SoftwareRevisionStringCharacteristic",
    "SoundPressureLevelCharacteristic",
    "SulfurDioxideConcentrationCharacteristic",
    "SupportedPowerRangeCharacteristic",
    "TemperatureCharacteristic",
    "TemperatureMeasurementCharacteristic",
    "TimeZoneCharacteristic",
    "TrueWindDirectionCharacteristic",
    "TrueWindSpeedCharacteristic",
    "TxPowerLevelCharacteristic",
    "UVIndexCharacteristic",
    "VOCConcentrationCharacteristic",
    "VoltageCharacteristic",
    "VoltageFrequencyCharacteristic",
    "VoltageSpecificationCharacteristic",
    "VoltageStatisticsCharacteristic",
    "WeightMeasurementCharacteristic",
    "WeightScaleFeatureCharacteristic",
    "WindChillCharacteristic",
]
