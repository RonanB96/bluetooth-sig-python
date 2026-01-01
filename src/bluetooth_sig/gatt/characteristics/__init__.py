"""Bluetooth SIG GATT characteristic registry.

Provides type-safe, registry-driven lookup for all supported
characteristics. Now encapsulated in CharacteristicRegistry class for
API clarity and extensibility.
"""

from __future__ import annotations

from .acceleration import AccelerationCharacteristic
from .activity_goal import ActivityGoalCharacteristic
from .aerobic_heart_rate_lower_limit import AerobicHeartRateLowerLimitCharacteristic
from .aerobic_heart_rate_upper_limit import AerobicHeartRateUpperLimitCharacteristic
from .aerobic_threshold import AerobicThresholdCharacteristic
from .age import AgeCharacteristic

# Import the registry components from the dedicated registry module
# Import all individual characteristic classes for backward compatibility
from .alert_category_id import AlertCategoryIdCharacteristic
from .alert_category_id_bit_mask import AlertCategoryIdBitMaskCharacteristic
from .alert_level import AlertLevelCharacteristic
from .alert_notification_control_point import AlertNotificationControlPointCharacteristic
from .altitude import AltitudeCharacteristic
from .ammonia_concentration import AmmoniaConcentrationCharacteristic
from .anaerobic_heart_rate_lower_limit import AnaerobicHeartRateLowerLimitCharacteristic
from .anaerobic_heart_rate_upper_limit import AnaerobicHeartRateUpperLimitCharacteristic
from .anaerobic_threshold import AnaerobicThresholdCharacteristic
from .apparent_energy_32 import ApparentEnergy32Characteristic
from .apparent_power import ApparentPowerCharacteristic
from .apparent_wind_direction import ApparentWindDirectionCharacteristic
from .apparent_wind_speed import ApparentWindSpeedCharacteristic
from .average_current import AverageCurrentCharacteristic
from .average_voltage import AverageVoltageCharacteristic
from .barometric_pressure_trend import BarometricPressureTrendCharacteristic
from .base import BaseCharacteristic
from .battery_critical_status import BatteryCriticalStatusCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .battery_level_status import BatteryLevelStatusCharacteristic
from .blood_pressure_feature import BloodPressureFeatureCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic
from .body_composition_measurement import BodyCompositionMeasurementCharacteristic
from .body_sensor_location import BodySensorLocation, BodySensorLocationCharacteristic
from .bond_management_control_point import BondManagementControlPointCharacteristic
from .bond_management_feature import BondManagementFeatureCharacteristic
from .caloric_intake import CaloricIntakeCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
from .csc_feature import CSCFeatureCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .current_time import CurrentTimeCharacteristic
from .cycling_power_control_point import CyclingPowerControlPointCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .cycling_power_measurement import CyclingPowerMeasurementCharacteristic
from .cycling_power_vector import CyclingPowerVectorCharacteristic
from .date_of_birth import DateOfBirthCharacteristic
from .date_of_threshold_assessment import DateOfThresholdAssessmentCharacteristic
from .device_info import (
    FirmwareRevisionStringCharacteristic,
    HardwareRevisionStringCharacteristic,
    SoftwareRevisionStringCharacteristic,
)
from .device_wearing_position import DeviceWearingPositionCharacteristic
from .dew_point import DewPointCharacteristic
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .elevation import ElevationCharacteristic
from .email_address import EmailAddressCharacteristic
from .fat_burn_heart_rate_lower_limit import FatBurnHeartRateLowerLimitCharacteristic
from .fat_burn_heart_rate_upper_limit import FatBurnHeartRateUpperLimitCharacteristic
from .first_name import FirstNameCharacteristic
from .five_zone_heart_rate_limits import FiveZoneHeartRateLimitsCharacteristic
from .force import ForceCharacteristic
from .four_zone_heart_rate_limits import FourZoneHeartRateLimitsCharacteristic
from .gender import Gender, GenderCharacteristic
from .generic_access import AppearanceCharacteristic, DeviceNameCharacteristic, ServiceChangedCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic, GlucoseFeatures
from .glucose_measurement import GlucoseMeasurementCharacteristic, GlucoseMeasurementFlags
from .glucose_measurement_context import GlucoseMeasurementContextCharacteristic, GlucoseMeasurementContextFlags
from .handedness import Handedness, HandednessCharacteristic
from .heart_rate_max import HeartRateMaxCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .heat_index import HeatIndexCharacteristic
from .height import HeightCharacteristic
from .high_intensity_exercise_threshold import HighIntensityExerciseThresholdCharacteristic
from .high_resolution_height import HighResolutionHeightCharacteristic
from .high_voltage import HighVoltageCharacteristic
from .hip_circumference import HipCircumferenceCharacteristic
from .humidity import HumidityCharacteristic
from .illuminance import IlluminanceCharacteristic
from .indoor_positioning_configuration import IndoorPositioningConfigurationCharacteristic
from .language import LanguageCharacteristic
from .last_name import LastNameCharacteristic
from .latitude import LatitudeCharacteristic
from .linear_position import LinearPositionCharacteristic
from .ln_control_point import LNControlPointCharacteristic
from .ln_feature import LNFeatureCharacteristic
from .local_east_coordinate import LocalEastCoordinateCharacteristic
from .local_north_coordinate import LocalNorthCoordinateCharacteristic
from .local_time_information import LocalTimeInformationCharacteristic
from .location_and_speed import LocationAndSpeedCharacteristic
from .location_name import LocationNameCharacteristic
from .longitude import LongitudeCharacteristic
from .magnetic_declination import MagneticDeclinationCharacteristic
from .magnetic_flux_density_2d import MagneticFluxDensity2DCharacteristic
from .magnetic_flux_density_3d import MagneticFluxDensity3DCharacteristic
from .manufacturer_name_string import ManufacturerNameStringCharacteristic
from .maximum_recommended_heart_rate import MaximumRecommendedHeartRateCharacteristic
from .methane_concentration import MethaneConcentrationCharacteristic
from .middle_name import MiddleNameCharacteristic
from .model_number_string import ModelNumberStringCharacteristic
from .navigation import NavigationCharacteristic
from .new_alert import NewAlertCharacteristic
from .nitrogen_dioxide_concentration import NitrogenDioxideConcentrationCharacteristic
from .noise import NoiseCharacteristic
from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
from .ozone_concentration import OzoneConcentrationCharacteristic
from .plx_features import PLXFeatureFlags, PLXFeaturesCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pollen_concentration import PollenConcentrationCharacteristic
from .position_quality import PositionQualityCharacteristic
from .power_specification import PowerSpecificationCharacteristic
from .preferred_units import PreferredUnitsCharacteristic, PreferredUnitsData
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rainfall import RainfallCharacteristic
from .reference_time_information import ReferenceTimeInformationCharacteristic
from .registry import CharacteristicName, CharacteristicRegistry, get_characteristic_class_map
from .resting_heart_rate import RestingHeartRateCharacteristic
from .rotational_speed import RotationalSpeedCharacteristic
from .rsc_feature import RSCFeatureCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .scan_interval_window import ScanIntervalWindowCharacteristic
from .sedentary_interval_notification import SedentaryIntervalNotificationCharacteristic
from .serial_number_string import SerialNumberStringCharacteristic
from .sport_type_for_aerobic_and_anaerobic_thresholds import (
    SportType,
    SportTypeForAerobicAndAnaerobicThresholdsCharacteristic,
)
from .stride_length import StrideLengthCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .supported_new_alert_category import SupportedNewAlertCategoryCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .supported_unread_alert_category import SupportedUnreadAlertCategoryCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .three_zone_heart_rate_limits import ThreeZoneHeartRateLimitsCharacteristic
from .time_update_control_point import TimeUpdateControlPointCharacteristic
from .time_update_state import TimeUpdateCurrentState, TimeUpdateResult, TimeUpdateState, TimeUpdateStateCharacteristic
from .time_with_dst import TimeWithDstCharacteristic
from .time_zone import TimeZoneCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .two_zone_heart_rate_limits import TwoZoneHeartRateLimitsCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .uncertainty import UncertaintyCharacteristic
from .unread_alert_status import UnreadAlertStatusCharacteristic
from .uv_index import UVIndexCharacteristic
from .vo2_max import VO2MaxCharacteristic
from .voc_concentration import VOCConcentrationCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .waist_circumference import WaistCircumferenceCharacteristic
from .weight import WeightCharacteristic
from .weight_measurement import WeightMeasurementCharacteristic
from .weight_scale_feature import WeightScaleFeatureCharacteristic
from .wind_chill import WindChillCharacteristic

__all__ = [
    # Registry components
    "CharacteristicName",
    "CharacteristicRegistry",
    "get_characteristic_class_map",
    # Base characteristic
    "BaseCharacteristic",
    # Individual characteristic classes (for backward compatibility)
    "AccelerationCharacteristic",
    "ActivityGoalCharacteristic",
    "AerobicHeartRateLowerLimitCharacteristic",
    "AerobicHeartRateUpperLimitCharacteristic",
    "AerobicThresholdCharacteristic",
    "AgeCharacteristic",
    "AlertCategoryIdBitMaskCharacteristic",
    "AlertCategoryIdCharacteristic",
    "AlertLevelCharacteristic",
    "AlertNotificationControlPointCharacteristic",
    "AltitudeCharacteristic",
    "AmmoniaConcentrationCharacteristic",
    "AnaerobicHeartRateLowerLimitCharacteristic",
    "AnaerobicHeartRateUpperLimitCharacteristic",
    "AnaerobicThresholdCharacteristic",
    "ApparentEnergy32Characteristic",
    "ApparentPowerCharacteristic",
    "ApparentWindDirectionCharacteristic",
    "ApparentWindSpeedCharacteristic",
    "AverageCurrentCharacteristic",
    "AverageVoltageCharacteristic",
    "BarometricPressureTrendCharacteristic",
    "BatteryCriticalStatusCharacteristic",
    "BatteryLevelCharacteristic",
    "BatteryLevelStatusCharacteristic",
    "BloodPressureFeatureCharacteristic",
    "BloodPressureMeasurementCharacteristic",
    "BodyCompositionFeatureCharacteristic",
    "BodyCompositionMeasurementCharacteristic",
    "BodySensorLocation",
    "BodySensorLocationCharacteristic",
    "BondManagementControlPointCharacteristic",
    "BondManagementFeatureCharacteristic",
    "CO2ConcentrationCharacteristic",
    "CaloricIntakeCharacteristic",
    "CSCFeatureCharacteristic",
    "CSCMeasurementCharacteristic",
    "CurrentTimeCharacteristic",
    "CyclingPowerControlPointCharacteristic",
    "CyclingPowerFeatureCharacteristic",
    "CyclingPowerMeasurementCharacteristic",
    "CyclingPowerVectorCharacteristic",
    "DateOfBirthCharacteristic",
    "DateOfThresholdAssessmentCharacteristic",
    "AppearanceCharacteristic",
    "DeviceNameCharacteristic",
    "DewPointCharacteristic",
    "DeviceWearingPositionCharacteristic",
    "ElectricCurrentCharacteristic",
    "ElectricCurrentRangeCharacteristic",
    "ElectricCurrentSpecificationCharacteristic",
    "ElectricCurrentStatisticsCharacteristic",
    "ElevationCharacteristic",
    "EmailAddressCharacteristic",
    "FatBurnHeartRateLowerLimitCharacteristic",
    "FatBurnHeartRateUpperLimitCharacteristic",
    "FirstNameCharacteristic",
    "FiveZoneHeartRateLimitsCharacteristic",
    "ForceCharacteristic",
    "FourZoneHeartRateLimitsCharacteristic",
    "Gender",
    "GenderCharacteristic",
    "FirmwareRevisionStringCharacteristic",
    "GlucoseFeatureCharacteristic",
    "GlucoseMeasurementCharacteristic",
    "GlucoseMeasurementContextCharacteristic",
    "GlucoseMeasurementContextFlags",
    "Handedness",
    "HandednessCharacteristic",
    "GlucoseMeasurementFlags",
    "GlucoseFeatures",
    "HeartRateMeasurementCharacteristic",
    "HeartRateMaxCharacteristic",
    "HeatIndexCharacteristic",
    "HeightCharacteristic",
    "HighIntensityExerciseThresholdCharacteristic",
    "HighResolutionHeightCharacteristic",
    "HighVoltageCharacteristic",
    "HumidityCharacteristic",
    "HipCircumferenceCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "IlluminanceCharacteristic",
    "IndoorPositioningConfigurationCharacteristic",
    "LastNameCharacteristic",
    "LatitudeCharacteristic",
    "LinearPositionCharacteristic",
    "LNControlPointCharacteristic",
    "LNFeatureCharacteristic",
    "LocalTimeInformationCharacteristic",
    "LocalNorthCoordinateCharacteristic",
    "LocalEastCoordinateCharacteristic",
    "LocationAndSpeedCharacteristic",
    "LocationNameCharacteristic",
    "LongitudeCharacteristic",
    "LanguageCharacteristic",
    "MagneticDeclinationCharacteristic",
    "MagneticFluxDensity2DCharacteristic",
    "MagneticFluxDensity3DCharacteristic",
    "ManufacturerNameStringCharacteristic",
    "MaximumRecommendedHeartRateCharacteristic",
    "MethaneConcentrationCharacteristic",
    "MiddleNameCharacteristic",
    "ModelNumberStringCharacteristic",
    "NavigationCharacteristic",
    "NewAlertCharacteristic",
    "NitrogenDioxideConcentrationCharacteristic",
    "NonMethaneVOCConcentrationCharacteristic",
    "OzoneConcentrationCharacteristic",
    "PM1ConcentrationCharacteristic",
    "PM10ConcentrationCharacteristic",
    "PM25ConcentrationCharacteristic",
    "PLXFeatureFlags",
    "PLXFeaturesCharacteristic",
    "PollenConcentrationCharacteristic",
    "PositionQualityCharacteristic",
    "PreferredUnitsCharacteristic",
    "PreferredUnitsData",
    "PowerSpecificationCharacteristic",
    "PressureCharacteristic",
    "PulseOximetryMeasurementCharacteristic",
    "RainfallCharacteristic",
    "ReferenceTimeInformationCharacteristic",
    "RestingHeartRateCharacteristic",
    "RotationalSpeedCharacteristic",
    "RSCFeatureCharacteristic",
    "RSCMeasurementCharacteristic",
    "SerialNumberStringCharacteristic",
    "ServiceChangedCharacteristic",
    "SoftwareRevisionStringCharacteristic",
    "NoiseCharacteristic",
    "SulfurDioxideConcentrationCharacteristic",
    "ScanIntervalWindowCharacteristic",
    "SedentaryIntervalNotificationCharacteristic",
    "SupportedNewAlertCategoryCharacteristic",
    "SupportedPowerRangeCharacteristic",
    "StrideLengthCharacteristic",
    "SupportedUnreadAlertCategoryCharacteristic",
    "SportType",
    "SportTypeForAerobicAndAnaerobicThresholdsCharacteristic",
    "TemperatureCharacteristic",
    "TemperatureMeasurementCharacteristic",
    "TimeUpdateControlPointCharacteristic",
    "TimeUpdateCurrentState",
    "TimeUpdateResult",
    "TimeUpdateState",
    "TimeUpdateStateCharacteristic",
    "TimeWithDstCharacteristic",
    "TimeZoneCharacteristic",
    "ThreeZoneHeartRateLimitsCharacteristic",
    "TwoZoneHeartRateLimitsCharacteristic",
    "TrueWindDirectionCharacteristic",
    "TrueWindSpeedCharacteristic",
    "TxPowerLevelCharacteristic",
    "UnreadAlertStatusCharacteristic",
    "UncertaintyCharacteristic",
    "UVIndexCharacteristic",
    "VO2MaxCharacteristic",
    "VOCConcentrationCharacteristic",
    "VoltageCharacteristic",
    "VoltageFrequencyCharacteristic",
    "VoltageSpecificationCharacteristic",
    "VoltageStatisticsCharacteristic",
    "WaistCircumferenceCharacteristic",
    "WeightCharacteristic",
    "WeightMeasurementCharacteristic",
    "WeightScaleFeatureCharacteristic",
    "WindChillCharacteristic",
]
