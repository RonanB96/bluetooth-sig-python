"""Bluetooth SIG GATT characteristic registry.

Provides type-safe, registry-driven lookup for all supported
characteristics. Now encapsulated in CharacteristicRegistry class for
API clarity and extensibility.
"""

from __future__ import annotations

from .acceleration import AccelerationCharacteristic
from .acceleration_3d import Acceleration3DCharacteristic
from .acceleration_detection_status import AccelerationDetectionStatusCharacteristic
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
from .appearance import AppearanceCharacteristic
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
from .boolean import BooleanCharacteristic
from .boot_keyboard_input_report import (
    BootKeyboardInputReportCharacteristic,
    BootKeyboardInputReportData,
    KeyboardModifiers,
)
from .boot_keyboard_output_report import BootKeyboardOutputReportCharacteristic, KeyboardLEDs
from .boot_mouse_input_report import BootMouseInputReportCharacteristic, BootMouseInputReportData, MouseButtons
from .caloric_intake import CaloricIntakeCharacteristic
from .carbon_monoxide_concentration import CarbonMonoxideConcentrationCharacteristic
from .chromaticity_coordinate import ChromaticityCoordinateCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
from .coefficient import CoefficientCharacteristic
from .correlated_color_temperature import CorrelatedColorTemperatureCharacteristic
from .count_16 import Count16Characteristic
from .count_24 import Count24Characteristic
from .csc_feature import CSCFeatureCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .current_time import CurrentTimeCharacteristic
from .cycling_power_control_point import CyclingPowerControlPointCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .cycling_power_measurement import CyclingPowerMeasurementCharacteristic
from .cycling_power_vector import CyclingPowerVectorCharacteristic
from .database_change_increment import DatabaseChangeIncrementCharacteristic
from .date_of_birth import DateOfBirthCharacteristic
from .date_of_threshold_assessment import DateOfThresholdAssessmentCharacteristic
from .date_time import DateTimeCharacteristic
from .day_date_time import DayDateTimeCharacteristic, DayDateTimeData
from .day_of_week import DayOfWeekCharacteristic
from .device_name import DeviceNameCharacteristic
from .device_wearing_position import DeviceWearingPositionCharacteristic
from .dew_point import DewPointCharacteristic
from .dst_offset import DstOffsetCharacteristic
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .elevation import ElevationCharacteristic
from .email_address import EmailAddressCharacteristic
from .exact_time_256 import ExactTime256Characteristic, ExactTime256Data
from .fat_burn_heart_rate_lower_limit import FatBurnHeartRateLowerLimitCharacteristic
from .fat_burn_heart_rate_upper_limit import FatBurnHeartRateUpperLimitCharacteristic
from .firmware_revision_string import FirmwareRevisionStringCharacteristic
from .first_name import FirstNameCharacteristic
from .five_zone_heart_rate_limits import FiveZoneHeartRateLimitsCharacteristic
from .force import ForceCharacteristic
from .four_zone_heart_rate_limits import FourZoneHeartRateLimitsCharacteristic
from .gender import Gender, GenderCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic, GlucoseFeatures
from .glucose_measurement import GlucoseMeasurementCharacteristic, GlucoseMeasurementFlags
from .glucose_measurement_context import GlucoseMeasurementContextCharacteristic, GlucoseMeasurementContextFlags
from .gust_factor import GustFactorCharacteristic
from .handedness import Handedness, HandednessCharacteristic
from .hardware_revision_string import HardwareRevisionStringCharacteristic
from .heart_rate_control_point import HeartRateControlPointCharacteristic
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
from .intermediate_temperature import IntermediateTemperatureCharacteristic
from .irradiance import IrradianceCharacteristic
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
from .measurement_interval import MeasurementIntervalCharacteristic
from .methane_concentration import MethaneConcentrationCharacteristic
from .middle_name import MiddleNameCharacteristic
from .model_number_string import ModelNumberStringCharacteristic
from .navigation import NavigationCharacteristic
from .new_alert import NewAlertCharacteristic
from .nitrogen_dioxide_concentration import NitrogenDioxideConcentrationCharacteristic
from .noise import NoiseCharacteristic
from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
from .ozone_concentration import OzoneConcentrationCharacteristic
from .peripheral_preferred_connection_parameters import (
    ConnectionParametersData,
    PeripheralPreferredConnectionParametersCharacteristic,
)
from .peripheral_privacy_flag import PeripheralPrivacyFlagCharacteristic
from .plx_features import PLXFeatureFlags, PLXFeaturesCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pnp_id import PnpIdCharacteristic, PnpIdData
from .pollen_concentration import PollenConcentrationCharacteristic
from .position_quality import PositionQualityCharacteristic
from .power_specification import PowerSpecificationCharacteristic
from .preferred_units import PreferredUnitsCharacteristic, PreferredUnitsData
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .rainfall import RainfallCharacteristic
from .reconnection_address import ReconnectionAddressCharacteristic
from .reference_time_information import ReferenceTimeInformationCharacteristic
from .registry import CharacteristicName, CharacteristicRegistry, get_characteristic_class_map
from .resting_heart_rate import RestingHeartRateCharacteristic
from .rotational_speed import RotationalSpeedCharacteristic
from .rsc_feature import RSCFeatureCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .scan_interval_window import ScanIntervalWindowCharacteristic
from .scan_refresh import ScanRefreshCharacteristic
from .sedentary_interval_notification import SedentaryIntervalNotificationCharacteristic
from .serial_number_string import SerialNumberStringCharacteristic
from .service_changed import ServiceChangedCharacteristic, ServiceChangedData
from .software_revision_string import SoftwareRevisionStringCharacteristic
from .sport_type_for_aerobic_and_anaerobic_thresholds import (
    SportType,
    SportTypeForAerobicAndAnaerobicThresholdsCharacteristic,
)
from .stride_length import StrideLengthCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .supported_new_alert_category import SupportedNewAlertCategoryCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .supported_unread_alert_category import SupportedUnreadAlertCategoryCharacteristic
from .system_id import SystemIdCharacteristic, SystemIdData
from .temperature import TemperatureCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .temperature_type import TemperatureTypeCharacteristic
from .three_zone_heart_rate_limits import ThreeZoneHeartRateLimitsCharacteristic
from .time_accuracy import TimeAccuracyCharacteristic
from .time_source import TimeSourceCharacteristic
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
from .user_index import UserIndexCharacteristic
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
    "Acceleration3DCharacteristic",
    # Individual characteristic classes (for backward compatibility)
    "AccelerationCharacteristic",
    "AccelerationDetectionStatusCharacteristic",
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
    "AppearanceCharacteristic",
    "AverageCurrentCharacteristic",
    "AverageVoltageCharacteristic",
    "BarometricPressureTrendCharacteristic",
    # Base characteristic
    "BaseCharacteristic",
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
    "BooleanCharacteristic",
    "BootKeyboardInputReportCharacteristic",
    "BootKeyboardInputReportData",
    "BootKeyboardOutputReportCharacteristic",
    "BootMouseInputReportCharacteristic",
    "BootMouseInputReportData",
    "CO2ConcentrationCharacteristic",
    "CSCFeatureCharacteristic",
    "CSCMeasurementCharacteristic",
    "CaloricIntakeCharacteristic",
    "CarbonMonoxideConcentrationCharacteristic",
    # Registry components
    "CharacteristicName",
    "CharacteristicRegistry",
    "ChromaticityCoordinateCharacteristic",
    "CoefficientCharacteristic",
    "ConnectionParametersData",
    "CorrelatedColorTemperatureCharacteristic",
    "Count16Characteristic",
    "Count24Characteristic",
    "CurrentTimeCharacteristic",
    "CyclingPowerControlPointCharacteristic",
    "CyclingPowerFeatureCharacteristic",
    "CyclingPowerMeasurementCharacteristic",
    "CyclingPowerVectorCharacteristic",
    "DatabaseChangeIncrementCharacteristic",
    "DateOfBirthCharacteristic",
    "DateOfThresholdAssessmentCharacteristic",
    "DateTimeCharacteristic",
    "DayDateTimeCharacteristic",
    "DayDateTimeData",
    "DayOfWeekCharacteristic",
    "DeviceNameCharacteristic",
    "DeviceWearingPositionCharacteristic",
    "DewPointCharacteristic",
    "DstOffsetCharacteristic",
    "ElectricCurrentCharacteristic",
    "ElectricCurrentRangeCharacteristic",
    "ElectricCurrentSpecificationCharacteristic",
    "ElectricCurrentStatisticsCharacteristic",
    "ElevationCharacteristic",
    "EmailAddressCharacteristic",
    "ExactTime256Characteristic",
    "ExactTime256Data",
    "FatBurnHeartRateLowerLimitCharacteristic",
    "FatBurnHeartRateUpperLimitCharacteristic",
    "FirmwareRevisionStringCharacteristic",
    "FirstNameCharacteristic",
    "FiveZoneHeartRateLimitsCharacteristic",
    "ForceCharacteristic",
    "FourZoneHeartRateLimitsCharacteristic",
    "Gender",
    "GenderCharacteristic",
    "GlucoseFeatureCharacteristic",
    "GlucoseFeatures",
    "GlucoseMeasurementCharacteristic",
    "GlucoseMeasurementContextCharacteristic",
    "GlucoseMeasurementContextFlags",
    "GlucoseMeasurementFlags",
    "GustFactorCharacteristic",
    "Handedness",
    "HandednessCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "HeartRateControlPointCharacteristic",
    "HeartRateMaxCharacteristic",
    "HeartRateMeasurementCharacteristic",
    "HeatIndexCharacteristic",
    "HeightCharacteristic",
    "HighIntensityExerciseThresholdCharacteristic",
    "HighResolutionHeightCharacteristic",
    "HighVoltageCharacteristic",
    "HipCircumferenceCharacteristic",
    "HumidityCharacteristic",
    "IlluminanceCharacteristic",
    "IndoorPositioningConfigurationCharacteristic",
    "IntermediateTemperatureCharacteristic",
    "IrradianceCharacteristic",
    "LNControlPointCharacteristic",
    "LNFeatureCharacteristic",
    "LanguageCharacteristic",
    "LastNameCharacteristic",
    "LatitudeCharacteristic",
    "LinearPositionCharacteristic",
    "LocalEastCoordinateCharacteristic",
    "LocalNorthCoordinateCharacteristic",
    "LocalTimeInformationCharacteristic",
    "LocationAndSpeedCharacteristic",
    "LocationNameCharacteristic",
    "LongitudeCharacteristic",
    "MagneticDeclinationCharacteristic",
    "MagneticFluxDensity2DCharacteristic",
    "MagneticFluxDensity3DCharacteristic",
    "ManufacturerNameStringCharacteristic",
    "MaximumRecommendedHeartRateCharacteristic",
    "MeasurementIntervalCharacteristic",
    "MethaneConcentrationCharacteristic",
    "MiddleNameCharacteristic",
    "ModelNumberStringCharacteristic",
    "NavigationCharacteristic",
    "NewAlertCharacteristic",
    "NitrogenDioxideConcentrationCharacteristic",
    "NoiseCharacteristic",
    "NonMethaneVOCConcentrationCharacteristic",
    "OzoneConcentrationCharacteristic",
    "PLXFeatureFlags",
    "PLXFeaturesCharacteristic",
    "PM1ConcentrationCharacteristic",
    "PM10ConcentrationCharacteristic",
    "PM25ConcentrationCharacteristic",
    "PeripheralPreferredConnectionParametersCharacteristic",
    "PeripheralPrivacyFlagCharacteristic",
    "PnpIdCharacteristic",
    "PnpIdData",
    "PollenConcentrationCharacteristic",
    "PositionQualityCharacteristic",
    "PowerSpecificationCharacteristic",
    "PreferredUnitsCharacteristic",
    "PreferredUnitsData",
    "PressureCharacteristic",
    "PulseOximetryMeasurementCharacteristic",
    "RSCFeatureCharacteristic",
    "RSCMeasurementCharacteristic",
    "RainfallCharacteristic",
    "ReconnectionAddressCharacteristic",
    "ReferenceTimeInformationCharacteristic",
    "RestingHeartRateCharacteristic",
    "RotationalSpeedCharacteristic",
    "ScanIntervalWindowCharacteristic",
    "ScanRefreshCharacteristic",
    "SedentaryIntervalNotificationCharacteristic",
    "SerialNumberStringCharacteristic",
    "ServiceChangedCharacteristic",
    "ServiceChangedData",
    "SoftwareRevisionStringCharacteristic",
    "SportType",
    "SportTypeForAerobicAndAnaerobicThresholdsCharacteristic",
    "StrideLengthCharacteristic",
    "SulfurDioxideConcentrationCharacteristic",
    "SupportedNewAlertCategoryCharacteristic",
    "SupportedPowerRangeCharacteristic",
    "SupportedUnreadAlertCategoryCharacteristic",
    "SystemIdCharacteristic",
    "SystemIdData",
    "TemperatureCharacteristic",
    "TemperatureMeasurementCharacteristic",
    "TemperatureTypeCharacteristic",
    "ThreeZoneHeartRateLimitsCharacteristic",
    "TimeAccuracyCharacteristic",
    "TimeSourceCharacteristic",
    "TimeUpdateControlPointCharacteristic",
    "TimeUpdateCurrentState",
    "TimeUpdateResult",
    "TimeUpdateState",
    "TimeUpdateStateCharacteristic",
    "TimeWithDstCharacteristic",
    "TimeZoneCharacteristic",
    "TrueWindDirectionCharacteristic",
    "TrueWindSpeedCharacteristic",
    "TwoZoneHeartRateLimitsCharacteristic",
    "TxPowerLevelCharacteristic",
    "UVIndexCharacteristic",
    "UncertaintyCharacteristic",
    "UnreadAlertStatusCharacteristic",
    "UserIndexCharacteristic",
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
    "get_characteristic_class_map",
]
