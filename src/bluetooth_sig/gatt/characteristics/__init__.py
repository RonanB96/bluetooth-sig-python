"""Bluetooth SIG GATT characteristic registry.

Provides type-safe, registry-driven lookup for all supported
characteristics. Now encapsulated in CharacteristicRegistry class for
API clarity and extensibility.
"""

from __future__ import annotations

from .acceleration import AccelerationCharacteristic
from .acceleration_3d import Acceleration3DCharacteristic
from .acceleration_detection_status import AccelerationDetectionStatusCharacteristic
from .active_preset_index import ActivePresetIndexCharacteristic
from .activity_goal import ActivityGoalCharacteristic
from .advertising_constant_tone_extension_interval import (
    AdvertisingConstantToneExtensionIntervalCharacteristic,
)
from .advertising_constant_tone_extension_minimum_length import (
    AdvertisingConstantToneExtensionMinimumLengthCharacteristic,
)
from .advertising_constant_tone_extension_minimum_transmit_count import (
    AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic,
)
from .advertising_constant_tone_extension_phy import (
    CTEPHY,
    AdvertisingConstantToneExtensionPhyCharacteristic,
)
from .advertising_constant_tone_extension_transmit_duration import (
    AdvertisingConstantToneExtensionTransmitDurationCharacteristic,
)
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
from .audio_input_description import AudioInputDescriptionCharacteristic
from .audio_input_status import AudioInputStatus, AudioInputStatusCharacteristic
from .audio_input_type import AudioInputType, AudioInputTypeCharacteristic
from .audio_location import AudioLocation, AudioLocationCharacteristic
from .audio_output_description import AudioOutputDescriptionCharacteristic
from .average_current import AverageCurrentCharacteristic
from .average_voltage import AverageVoltageCharacteristic
from .barometric_pressure_trend import BarometricPressureTrendCharacteristic
from .base import BaseCharacteristic
from .battery_critical_status import BatteryCriticalStatusCharacteristic
from .battery_energy_status import BatteryEnergyStatusCharacteristic
from .battery_health_information import BatteryHealthInformationCharacteristic
from .battery_health_status import BatteryHealthStatusCharacteristic
from .battery_information import BatteryInformationCharacteristic
from .battery_level import BatteryLevelCharacteristic
from .battery_level_status import BatteryLevelStatusCharacteristic
from .battery_time_status import BatteryTimeStatusCharacteristic
from .bearer_provider_name import BearerProviderNameCharacteristic
from .bearer_signal_strength import BearerSignalStrengthCharacteristic
from .bearer_signal_strength_reporting_interval import BearerSignalStrengthReportingIntervalCharacteristic
from .bearer_technology import BearerTechnology, BearerTechnologyCharacteristic
from .bearer_uci import BearerUCICharacteristic
from .bearer_uri_schemes_supported_list import BearerURISchemesCharacteristic
from .bgr_features import BGRFeatures, BGRFeaturesCharacteristic
from .bgs_features import BGSFeatures, BGSFeaturesCharacteristic
from .blood_pressure_feature import BloodPressureFeatureCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .blood_pressure_record import BloodPressureRecordCharacteristic, BloodPressureRecordData
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
from .call_friendly_name import CallFriendlyNameCharacteristic
from .caloric_intake import CaloricIntakeCharacteristic
from .carbon_monoxide_concentration import CarbonMonoxideConcentrationCharacteristic
from .central_address_resolution import CentralAddressResolutionCharacteristic, CentralAddressResolutionSupport
from .cgm_feature import CGMFeatureCharacteristic, CGMFeatureData, CGMFeatureFlags, CGMSampleLocation, CGMType
from .cgm_measurement import (
    CGMCalTempOctet,
    CGMMeasurementCharacteristic,
    CGMMeasurementData,
    CGMMeasurementFlags,
    CGMMeasurementRecord,
    CGMSensorStatusOctet,
    CGMWarningOctet,
)
from .cgm_session_run_time import CGMSessionRunTimeCharacteristic, CGMSessionRunTimeData
from .cgm_session_start_time import CGMSessionStartTimeCharacteristic, CGMSessionStartTimeData
from .cgm_status import CGMStatusCharacteristic, CGMStatusData, CGMStatusFlags
from .chromatic_distance_from_planckian import ChromaticDistanceFromPlanckianCharacteristic
from .chromaticity_coordinate import ChromaticityCoordinateCharacteristic
from .chromaticity_coordinates import ChromaticityCoordinatesCharacteristic, ChromaticityCoordinatesData
from .chromaticity_in_cct_and_duv_values import (
    ChromaticityInCCTAndDuvData,
    ChromaticityInCCTAndDuvValuesCharacteristic,
)
from .chromaticity_tolerance import ChromaticityToleranceCharacteristic
from .cie_13_3_1995_color_rendering_index import CIE133ColorRenderingIndexCharacteristic
from .client_supported_features import ClientFeatures, ClientSupportedFeaturesCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
from .coefficient import CoefficientCharacteristic
from .constant_tone_extension_enable import ConstantToneExtensionEnableCharacteristic, CTEEnableState
from .contact_status_8 import ContactStatus, ContactStatus8Characteristic
from .content_control_id import ContentControlIdCharacteristic
from .coordinated_set_size import CoordinatedSetSizeCharacteristic
from .correlated_color_temperature import CorrelatedColorTemperatureCharacteristic
from .cosine_of_the_angle import CosineOfTheAngleCharacteristic
from .count_16 import Count16Characteristic
from .count_24 import Count24Characteristic
from .country_code import CountryCodeCharacteristic
from .cross_trainer_data import CrossTrainerData, CrossTrainerDataCharacteristic
from .csc_feature import CSCFeatureCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .current_elapsed_time import (
    CurrentElapsedTimeCharacteristic,
    CurrentElapsedTimeData,
    ElapsedTimeFlags,
    TimeResolution,
)
from .current_time import CurrentTimeCharacteristic
from .cycling_power_control_point import CyclingPowerControlPointCharacteristic
from .cycling_power_feature import CyclingPowerFeatureCharacteristic
from .cycling_power_measurement import CyclingPowerMeasurementCharacteristic
from .cycling_power_vector import CyclingPowerVectorCharacteristic
from .database_change_increment import DatabaseChangeIncrementCharacteristic
from .database_hash import DatabaseHashCharacteristic
from .date_of_birth import DateOfBirthCharacteristic
from .date_of_threshold_assessment import DateOfThresholdAssessmentCharacteristic
from .date_time import DateTimeCharacteristic
from .date_utc import DateUtcCharacteristic
from .day_date_time import DayDateTimeCharacteristic, DayDateTimeData
from .day_of_week import DayOfWeekCharacteristic
from .device_name import DeviceNameCharacteristic
from .device_wearing_position import DeviceWearingPositionCharacteristic
from .dew_point import DewPointCharacteristic
from .door_window_status import DoorWindowOpenStatus, DoorWindowStatusCharacteristic
from .dst_offset import DstOffsetCharacteristic
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .elevation import ElevationCharacteristic
from .email_address import EmailAddressCharacteristic
from .emergency_id import EmergencyIdCharacteristic
from .emergency_text import EmergencyTextCharacteristic
from .energy import EnergyCharacteristic
from .energy_32 import Energy32Characteristic
from .energy_in_a_period_of_day import (
    EnergyInAPeriodOfDayCharacteristic,
    EnergyInAPeriodOfDayData,
)
from .enhanced_blood_pressure_measurement import (
    EnhancedBloodPressureData,
    EnhancedBloodPressureFlags,
    EnhancedBloodPressureMeasurementCharacteristic,
    EpochYear,
)
from .enhanced_intermediate_cuff_pressure import (
    EnhancedIntermediateCuffPressureCharacteristic,
    EnhancedIntermediateCuffPressureData,
)
from .estimated_service_date import EstimatedServiceDateCharacteristic
from .event_statistics import EventStatisticsCharacteristic, EventStatisticsData
from .exact_time_256 import ExactTime256Characteristic, ExactTime256Data
from .fat_burn_heart_rate_lower_limit import FatBurnHeartRateLowerLimitCharacteristic
from .fat_burn_heart_rate_upper_limit import FatBurnHeartRateUpperLimitCharacteristic
from .firmware_revision_string import FirmwareRevisionStringCharacteristic
from .first_name import FirstNameCharacteristic
from .first_use_date import FirstUseDateCharacteristic
from .five_zone_heart_rate_limits import FiveZoneHeartRateLimitsCharacteristic
from .fixed_string_8 import FixedString8Characteristic
from .fixed_string_16 import FixedString16Characteristic
from .fixed_string_24 import FixedString24Characteristic
from .fixed_string_36 import FixedString36Characteristic
from .fixed_string_64 import FixedString64Characteristic
from .force import ForceCharacteristic
from .four_zone_heart_rate_limits import FourZoneHeartRateLimitsCharacteristic
from .gender import Gender, GenderCharacteristic
from .generic_level import GenericLevelCharacteristic
from .global_trade_item_number import GlobalTradeItemNumberCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic, GlucoseFeatures
from .glucose_measurement import GlucoseMeasurementCharacteristic, GlucoseMeasurementFlags
from .glucose_measurement_context import GlucoseMeasurementContextCharacteristic, GlucoseMeasurementContextFlags
from .gmap_role import GMAPRole, GMAPRoleCharacteristic
from .gust_factor import GustFactorCharacteristic
from .handedness import Handedness, HandednessCharacteristic
from .hardware_revision_string import HardwareRevisionStringCharacteristic
from .health_sensor_features import HealthSensorFeatures, HealthSensorFeaturesCharacteristic
from .hearing_aid_features import HearingAidFeatures, HearingAidFeaturesCharacteristic
from .heart_rate_control_point import HeartRateControlPointCharacteristic
from .heart_rate_max import HeartRateMaxCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .heat_index import HeatIndexCharacteristic
from .height import HeightCharacteristic
from .high_intensity_exercise_threshold import HighIntensityExerciseThresholdCharacteristic
from .high_resolution_height import HighResolutionHeightCharacteristic
from .high_temperature import HighTemperatureCharacteristic
from .high_voltage import HighVoltageCharacteristic
from .hip_circumference import HipCircumferenceCharacteristic
from .https_security import HttpsSecurityCharacteristic, HttpsSecurityState
from .humidity import HumidityCharacteristic
from .humidity_8 import Humidity8Characteristic
from .ieee_11073_20601_regulatory_certification_data_list import (
    IEEE11073RegulatoryData,
    IEEE1107320601RegulatoryCharacteristic,
)
from .illuminance import IlluminanceCharacteristic
from .illuminance_16 import Illuminance16Characteristic
from .indoor_bike_data import IndoorBikeData, IndoorBikeDataCharacteristic
from .indoor_positioning_configuration import IndoorPositioningConfigurationCharacteristic
from .intermediate_temperature import IntermediateTemperatureCharacteristic
from .irradiance import IrradianceCharacteristic
from .language import LanguageCharacteristic
from .last_name import LastNameCharacteristic
from .latitude import LatitudeCharacteristic
from .le_gatt_security_levels import (
    LEGATTSecurityLevelsCharacteristic,
    LESecurityMode,
    LESecurityModeLevel,
    SecurityLevelRequirement,
)
from .length import LengthCharacteristic
from .light_distribution import LightDistributionCharacteristic, LightDistributionType
from .light_output import LightOutputCharacteristic
from .light_source_type import LightSourceTypeCharacteristic, LightSourceTypeValue
from .linear_position import LinearPositionCharacteristic
from .ln_control_point import LNControlPointCharacteristic
from .ln_feature import LNFeatureCharacteristic
from .local_east_coordinate import LocalEastCoordinateCharacteristic
from .local_north_coordinate import LocalNorthCoordinateCharacteristic
from .local_time_information import LocalTimeInformationCharacteristic
from .location_and_speed import LocationAndSpeedCharacteristic
from .location_name import LocationNameCharacteristic
from .longitude import LongitudeCharacteristic
from .luminous_efficacy import LuminousEfficacyCharacteristic
from .luminous_energy import LuminousEnergyCharacteristic
from .luminous_exposure import LuminousExposureCharacteristic
from .luminous_flux import LuminousFluxCharacteristic
from .luminous_flux_range import LuminousFluxRangeCharacteristic, LuminousFluxRangeData
from .luminous_intensity import LuminousIntensityCharacteristic
from .magnetic_declination import MagneticDeclinationCharacteristic
from .magnetic_flux_density_2d import MagneticFluxDensity2DCharacteristic
from .magnetic_flux_density_3d import MagneticFluxDensity3DCharacteristic
from .manufacturer_name_string import ManufacturerNameStringCharacteristic
from .mass_flow import MassFlowCharacteristic
from .maximum_recommended_heart_rate import MaximumRecommendedHeartRateCharacteristic
from .measurement_interval import MeasurementIntervalCharacteristic
from .media_control_point_opcodes_supported import (
    MediaControlPointOpcodes,
    MediaControlPointOpcodesSupportedCharacteristic,
)
from .media_player_icon_url import MediaPlayerIconURLCharacteristic
from .media_player_name import MediaPlayerNameCharacteristic
from .media_state import MediaState, MediaStateCharacteristic
from .methane_concentration import MethaneConcentrationCharacteristic
from .middle_name import MiddleNameCharacteristic
from .model_number_string import ModelNumberStringCharacteristic
from .mute import MuteCharacteristic, MuteState
from .navigation import NavigationCharacteristic
from .new_alert import NewAlertCharacteristic
from .nitrogen_dioxide_concentration import NitrogenDioxideConcentrationCharacteristic
from .noise import NoiseCharacteristic
from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
from .object_first_created import ObjectFirstCreatedCharacteristic
from .object_id import ObjectIdCharacteristic
from .object_last_modified import ObjectLastModifiedCharacteristic
from .object_name import ObjectNameCharacteristic
from .object_type import ObjectTypeCharacteristic
from .ots_feature import OACPFeatures, OLCPFeatures, OTSFeatureCharacteristic, OTSFeatureData
from .ozone_concentration import OzoneConcentrationCharacteristic
from .perceived_lightness import PerceivedLightnessCharacteristic
from .percentage_8 import Percentage8Characteristic
from .percentage_8_steps import Percentage8StepsCharacteristic
from .peripheral_preferred_connection_parameters import (
    ConnectionParametersData,
    PeripheralPreferredConnectionParametersCharacteristic,
)
from .peripheral_privacy_flag import PeripheralPrivacyFlagCharacteristic, PeripheralPrivacyState
from .playback_speed import PlaybackSpeedCharacteristic
from .playing_order import PlayingOrder, PlayingOrderCharacteristic
from .playing_orders_supported import PlayingOrdersSupported, PlayingOrdersSupportedCharacteristic
from .plx_features import PLXFeatureFlags, PLXFeaturesCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pnp_id import PnpIdCharacteristic, PnpIdData
from .pollen_concentration import PollenConcentrationCharacteristic
from .position_quality import PositionQualityCharacteristic
from .power import PowerCharacteristic
from .power_specification import PowerSpecificationCharacteristic
from .precise_acceleration_3d import PreciseAcceleration3DCharacteristic
from .preferred_units import PreferredUnitsCharacteristic, PreferredUnitsData
from .pressure import PressureCharacteristic
from .pulse_oximetry_measurement import PulseOximetryMeasurementCharacteristic
from .pushbutton_status_8 import (
    ButtonStatus,
    PushbuttonStatus8Characteristic,
    PushbuttonStatus8Data,
)
from .rainfall import RainfallCharacteristic
from .rc_feature import RCFeature, RCFeatureCharacteristic
from .reconnection_address import ReconnectionAddressCharacteristic
from .reference_time_information import ReferenceTimeInformationCharacteristic
from .registry import CharacteristicName, CharacteristicRegistry, get_characteristic_class_map
from .relative_runtime_in_a_correlated_color_temperature_range import (
    RelativeRuntimeInACCTRangeData,
    RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic,
)
from .relative_runtime_in_a_current_range import (
    RelativeRuntimeInACurrentRangeCharacteristic,
    RelativeRuntimeInACurrentRangeData,
)
from .relative_runtime_in_a_generic_level_range import (
    RelativeRuntimeInAGenericLevelRangeCharacteristic,
    RelativeRuntimeInAGenericLevelRangeData,
)
from .relative_value_in_a_period_of_day import (
    RelativeValueInAPeriodOfDayCharacteristic,
    RelativeValueInAPeriodOfDayData,
)
from .relative_value_in_a_temperature_range import (
    RelativeValueInATemperatureRangeCharacteristic,
    RelativeValueInATemperatureRangeData,
)
from .relative_value_in_a_voltage_range import (
    RelativeValueInAVoltageRangeCharacteristic,
    RelativeValueInAVoltageRangeData,
)
from .relative_value_in_an_illuminance_range import (
    RelativeValueInAnIlluminanceRangeCharacteristic,
    RelativeValueInAnIlluminanceRangeData,
)
from .resolvable_private_address_only import ResolvablePrivateAddressOnlyCharacteristic
from .resting_heart_rate import RestingHeartRateCharacteristic
from .rotational_speed import RotationalSpeedCharacteristic
from .rower_data import RowerData, RowerDataCharacteristic
from .rsc_feature import RSCFeatureCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .scan_interval_window import ScanIntervalWindowCharacteristic
from .scan_refresh import ScanRefreshCharacteristic
from .sedentary_interval_notification import SedentaryIntervalNotificationCharacteristic
from .seeking_speed import SeekingSpeedCharacteristic
from .sensor_location import SensorLocationCharacteristic, SensorLocationValue
from .serial_number_string import SerialNumberStringCharacteristic
from .server_supported_features import ServerFeatures, ServerSupportedFeaturesCharacteristic
from .service_changed import ServiceChangedCharacteristic, ServiceChangedData
from .set_member_lock import SetMemberLockCharacteristic, SetMemberLockState
from .set_member_rank import SetMemberRankCharacteristic
from .software_revision_string import SoftwareRevisionStringCharacteristic
from .sport_type_for_aerobic_and_anaerobic_thresholds import (
    SportType,
    SportTypeForAerobicAndAnaerobicThresholdsCharacteristic,
)
from .stair_climber_data import StairClimberData, StairClimberDataCharacteristic
from .status_flags import StatusFlags, StatusFlagsCharacteristic
from .step_climber_data import StepClimberData, StepClimberDataCharacteristic
from .stride_length import StrideLengthCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .sulfur_hexafluoride_concentration import SulfurHexafluorideConcentrationCharacteristic
from .supported_heart_rate_range import (
    SupportedHeartRateRangeCharacteristic,
    SupportedHeartRateRangeData,
)
from .supported_inclination_range import (
    SupportedInclinationRangeCharacteristic,
    SupportedInclinationRangeData,
)
from .supported_new_alert_category import SupportedNewAlertCategoryCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .supported_resistance_level_range import (
    SupportedResistanceLevelRangeCharacteristic,
    SupportedResistanceLevelRangeData,
)
from .supported_speed_range import SupportedSpeedRangeCharacteristic, SupportedSpeedRangeData
from .supported_unread_alert_category import SupportedUnreadAlertCategoryCharacteristic
from .system_id import SystemIdCharacteristic, SystemIdData
from .temperature import TemperatureCharacteristic
from .temperature_8 import Temperature8Characteristic
from .temperature_8_in_a_period_of_day import (
    Temperature8InAPeriodOfDayCharacteristic,
    Temperature8InAPeriodOfDayData,
)
from .temperature_8_statistics import (
    Temperature8StatisticsCharacteristic,
    Temperature8StatisticsData,
)
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .temperature_range import TemperatureRangeCharacteristic, TemperatureRangeData
from .temperature_statistics import (
    TemperatureStatisticsCharacteristic,
    TemperatureStatisticsData,
)
from .temperature_type import TemperatureTypeCharacteristic
from .termination_reason import TerminationReason, TerminationReasonCharacteristic
from .three_zone_heart_rate_limits import ThreeZoneHeartRateLimitsCharacteristic
from .time_accuracy import TimeAccuracyCharacteristic
from .time_decihour_8 import TimeDecihour8Characteristic
from .time_exponential_8 import TimeExponential8Characteristic
from .time_hour_24 import TimeHour24Characteristic
from .time_millisecond_24 import TimeMillisecond24Characteristic
from .time_second_8 import TimeSecond8Characteristic
from .time_second_16 import TimeSecond16Characteristic
from .time_second_32 import TimeSecond32Characteristic
from .time_source import TimeSourceCharacteristic
from .time_update_control_point import TimeUpdateControlPointCharacteristic
from .time_update_state import TimeUpdateCurrentState, TimeUpdateResult, TimeUpdateState, TimeUpdateStateCharacteristic
from .time_with_dst import TimeWithDstCharacteristic
from .time_zone import TimeZoneCharacteristic
from .tmap_role import TMAPRole, TMAPRoleCharacteristic
from .torque import TorqueCharacteristic
from .track_changed import TrackChangedCharacteristic
from .track_duration import TrackDurationCharacteristic
from .track_position import TrackPositionCharacteristic
from .track_title import TrackTitleCharacteristic
from .treadmill_data import TreadmillData, TreadmillDataCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .two_zone_heart_rate_limits import TwoZoneHeartRateLimitsCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .ugg_features import UGGFeatures, UGGFeaturesCharacteristic
from .ugt_features import UGTFeatures, UGTFeaturesCharacteristic
from .uncertainty import UncertaintyCharacteristic
from .unread_alert_status import UnreadAlertStatusCharacteristic
from .uri import URICharacteristic
from .user_index import UserIndexCharacteristic
from .uv_index import UVIndexCharacteristic
from .vo2_max import VO2MaxCharacteristic
from .voc_concentration import VOCConcentrationCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .volume_flags import VolumeFlags, VolumeFlagsCharacteristic
from .volume_flow import VolumeFlowCharacteristic
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
    "ActivePresetIndexCharacteristic",
    "ActivityGoalCharacteristic",
    "AerobicHeartRateLowerLimitCharacteristic",
    "AerobicHeartRateUpperLimitCharacteristic",
    "AerobicThresholdCharacteristic",
    "AdvertisingConstantToneExtensionIntervalCharacteristic",
    "AdvertisingConstantToneExtensionMinimumLengthCharacteristic",
    "AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic",
    "AdvertisingConstantToneExtensionPhyCharacteristic",
    "AdvertisingConstantToneExtensionTransmitDurationCharacteristic",
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
    "AudioInputDescriptionCharacteristic",
    "AudioInputStatus",
    "AudioInputStatusCharacteristic",
    "AudioInputType",
    "AudioInputTypeCharacteristic",
    "AudioLocation",
    "AudioLocationCharacteristic",
    "AudioOutputDescriptionCharacteristic",
    "AverageCurrentCharacteristic",
    "AverageVoltageCharacteristic",
    "BarometricPressureTrendCharacteristic",
    # Base characteristic
    "BaseCharacteristic",
    "BatteryCriticalStatusCharacteristic",
    "BatteryEnergyStatusCharacteristic",
    "BatteryHealthInformationCharacteristic",
    "BatteryHealthStatusCharacteristic",
    "BatteryInformationCharacteristic",
    "BatteryLevelCharacteristic",
    "BatteryLevelStatusCharacteristic",
    "BatteryTimeStatusCharacteristic",
    "BearerProviderNameCharacteristic",
    "BearerSignalStrengthCharacteristic",
    "BearerSignalStrengthReportingIntervalCharacteristic",
    "BearerTechnology",
    "BearerTechnologyCharacteristic",
    "BearerUCICharacteristic",
    "BearerURISchemesCharacteristic",
    "BGRFeatures",
    "BGRFeaturesCharacteristic",
    "BGSFeatures",
    "BGSFeaturesCharacteristic",
    "BloodPressureFeatureCharacteristic",
    "BloodPressureMeasurementCharacteristic",
    "BloodPressureRecordCharacteristic",
    "BloodPressureRecordData",
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
    "CGMFeatureCharacteristic",
    "CGMFeatureData",
    "CGMFeatureFlags",
    "CGMCalTempOctet",
    "CGMMeasurementCharacteristic",
    "CGMMeasurementData",
    "CGMMeasurementFlags",
    "CGMMeasurementRecord",
    "CGMSampleLocation",
    "CGMSensorStatusOctet",
    "CGMSessionRunTimeCharacteristic",
    "CGMSessionRunTimeData",
    "CGMSessionStartTimeCharacteristic",
    "CGMSessionStartTimeData",
    "CGMStatusCharacteristic",
    "CGMStatusData",
    "CGMStatusFlags",
    "CGMType",
    "CGMWarningOctet",
    "CO2ConcentrationCharacteristic",
    "CSCFeatureCharacteristic",
    "CSCMeasurementCharacteristic",
    "CallFriendlyNameCharacteristic",
    "CaloricIntakeCharacteristic",
    "CarbonMonoxideConcentrationCharacteristic",
    "CentralAddressResolutionCharacteristic",
    "CentralAddressResolutionSupport",
    # Registry components
    "CharacteristicName",
    "CharacteristicRegistry",
    "ClientFeatures",
    "ClientSupportedFeaturesCharacteristic",
    "ChromaticityCoordinateCharacteristic",
    "ChromaticityCoordinatesCharacteristic",
    "ChromaticityCoordinatesData",
    "ChromaticityInCCTAndDuvData",
    "ChromaticityInCCTAndDuvValuesCharacteristic",
    "ChromaticityToleranceCharacteristic",
    "ChromaticDistanceFromPlanckianCharacteristic",
    "CIE133ColorRenderingIndexCharacteristic",
    "CoefficientCharacteristic",
    "ConnectionParametersData",
    "ContactStatus",
    "ContactStatus8Characteristic",
    "ContentControlIdCharacteristic",
    "CoordinatedSetSizeCharacteristic",
    "CorrelatedColorTemperatureCharacteristic",
    "CosineOfTheAngleCharacteristic",
    "Count16Characteristic",
    "Count24Characteristic",
    "CTEPHY",
    "CTEEnableState",
    "ConstantToneExtensionEnableCharacteristic",
    "CountryCodeCharacteristic",
    "CrossTrainerData",
    "CrossTrainerDataCharacteristic",
    "CurrentElapsedTimeCharacteristic",
    "CurrentElapsedTimeData",
    "CurrentTimeCharacteristic",
    "CyclingPowerControlPointCharacteristic",
    "CyclingPowerFeatureCharacteristic",
    "CyclingPowerMeasurementCharacteristic",
    "CyclingPowerVectorCharacteristic",
    "DatabaseChangeIncrementCharacteristic",
    "DatabaseHashCharacteristic",
    "DateOfBirthCharacteristic",
    "DateOfThresholdAssessmentCharacteristic",
    "DateTimeCharacteristic",
    "DateUtcCharacteristic",
    "DayDateTimeCharacteristic",
    "DayDateTimeData",
    "DayOfWeekCharacteristic",
    "DeviceNameCharacteristic",
    "DeviceWearingPositionCharacteristic",
    "DewPointCharacteristic",
    "DoorWindowOpenStatus",
    "DoorWindowStatusCharacteristic",
    "DstOffsetCharacteristic",
    "ElectricCurrentCharacteristic",
    "ElectricCurrentRangeCharacteristic",
    "ElectricCurrentSpecificationCharacteristic",
    "ElectricCurrentStatisticsCharacteristic",
    "ElevationCharacteristic",
    "EmailAddressCharacteristic",
    "EmergencyIdCharacteristic",
    "EmergencyTextCharacteristic",
    "EnergyCharacteristic",
    "Energy32Characteristic",
    "EnergyInAPeriodOfDayCharacteristic",
    "EnergyInAPeriodOfDayData",
    "EnhancedBloodPressureData",
    "EnhancedBloodPressureFlags",
    "EnhancedBloodPressureMeasurementCharacteristic",
    "EnhancedIntermediateCuffPressureCharacteristic",
    "EnhancedIntermediateCuffPressureData",
    "EpochYear",
    "EstimatedServiceDateCharacteristic",
    "ExactTime256Characteristic",
    "ExactTime256Data",
    "EventStatisticsCharacteristic",
    "EventStatisticsData",
    "FatBurnHeartRateLowerLimitCharacteristic",
    "FatBurnHeartRateUpperLimitCharacteristic",
    "FirmwareRevisionStringCharacteristic",
    "FirstNameCharacteristic",
    "FirstUseDateCharacteristic",
    "FiveZoneHeartRateLimitsCharacteristic",
    "FixedString8Characteristic",
    "FixedString16Characteristic",
    "FixedString24Characteristic",
    "FixedString36Characteristic",
    "FixedString64Characteristic",
    "ForceCharacteristic",
    "FourZoneHeartRateLimitsCharacteristic",
    "Gender",
    "GenderCharacteristic",
    "GenericLevelCharacteristic",
    "GlobalTradeItemNumberCharacteristic",
    "GlucoseFeatureCharacteristic",
    "GlucoseFeatures",
    "GlucoseMeasurementCharacteristic",
    "GlucoseMeasurementContextCharacteristic",
    "GlucoseMeasurementContextFlags",
    "GlucoseMeasurementFlags",
    "GMAPRole",
    "GMAPRoleCharacteristic",
    "GustFactorCharacteristic",
    "Handedness",
    "HandednessCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "HealthSensorFeatures",
    "HealthSensorFeaturesCharacteristic",
    "HearingAidFeatures",
    "HearingAidFeaturesCharacteristic",
    "HeartRateControlPointCharacteristic",
    "HeartRateMaxCharacteristic",
    "HeartRateMeasurementCharacteristic",
    "HeatIndexCharacteristic",
    "HeightCharacteristic",
    "HighIntensityExerciseThresholdCharacteristic",
    "HighResolutionHeightCharacteristic",
    "HighTemperatureCharacteristic",
    "HighVoltageCharacteristic",
    "HipCircumferenceCharacteristic",
    "HumidityCharacteristic",
    "Humidity8Characteristic",
    "HttpsSecurityCharacteristic",
    "HttpsSecurityState",
    "IEEE1107320601RegulatoryCharacteristic",
    "IEEE11073RegulatoryData",
    "IlluminanceCharacteristic",
    "Illuminance16Characteristic",
    "IndoorBikeData",
    "IndoorBikeDataCharacteristic",
    "IndoorPositioningConfigurationCharacteristic",
    "IntermediateTemperatureCharacteristic",
    "ElapsedTimeFlags",
    "TimeResolution",
    "IrradianceCharacteristic",
    "LNControlPointCharacteristic",
    "LNFeatureCharacteristic",
    "LanguageCharacteristic",
    "LastNameCharacteristic",
    "LatitudeCharacteristic",
    "SecurityLevelRequirement",
    "LEGATTSecurityLevelsCharacteristic",
    "LESecurityMode",
    "LESecurityModeLevel",
    "LengthCharacteristic",
    "LightDistributionCharacteristic",
    "LightDistributionType",
    "LightOutputCharacteristic",
    "LightSourceTypeCharacteristic",
    "LightSourceTypeValue",
    "LinearPositionCharacteristic",
    "LocalEastCoordinateCharacteristic",
    "LocalNorthCoordinateCharacteristic",
    "LocalTimeInformationCharacteristic",
    "LocationAndSpeedCharacteristic",
    "LocationNameCharacteristic",
    "LongitudeCharacteristic",
    "LuminousEfficacyCharacteristic",
    "LuminousEnergyCharacteristic",
    "LuminousExposureCharacteristic",
    "LuminousFluxCharacteristic",
    "LuminousFluxRangeCharacteristic",
    "LuminousFluxRangeData",
    "LuminousIntensityCharacteristic",
    "MagneticDeclinationCharacteristic",
    "MagneticFluxDensity2DCharacteristic",
    "MagneticFluxDensity3DCharacteristic",
    "ManufacturerNameStringCharacteristic",
    "MassFlowCharacteristic",
    "MaximumRecommendedHeartRateCharacteristic",
    "MeasurementIntervalCharacteristic",
    "MediaControlPointOpcodes",
    "MediaControlPointOpcodesSupportedCharacteristic",
    "MediaPlayerIconURLCharacteristic",
    "MediaPlayerNameCharacteristic",
    "MediaState",
    "MediaStateCharacteristic",
    "MethaneConcentrationCharacteristic",
    "MiddleNameCharacteristic",
    "ModelNumberStringCharacteristic",
    "MuteCharacteristic",
    "MuteState",
    "NavigationCharacteristic",
    "NewAlertCharacteristic",
    "NitrogenDioxideConcentrationCharacteristic",
    "NoiseCharacteristic",
    "NonMethaneVOCConcentrationCharacteristic",
    "ObjectFirstCreatedCharacteristic",
    "ObjectIdCharacteristic",
    "ObjectLastModifiedCharacteristic",
    "ObjectNameCharacteristic",
    "ObjectTypeCharacteristic",
    "OACPFeatures",
    "OLCPFeatures",
    "OTSFeatureCharacteristic",
    "OTSFeatureData",
    "OzoneConcentrationCharacteristic",
    "PLXFeatureFlags",
    "PLXFeaturesCharacteristic",
    "PM1ConcentrationCharacteristic",
    "PM10ConcentrationCharacteristic",
    "PM25ConcentrationCharacteristic",
    "PeripheralPreferredConnectionParametersCharacteristic",
    "PeripheralPrivacyFlagCharacteristic",
    "PeripheralPrivacyState",
    "PerceivedLightnessCharacteristic",
    "Percentage8Characteristic",
    "Percentage8StepsCharacteristic",
    "PlaybackSpeedCharacteristic",
    "PlayingOrder",
    "PlayingOrderCharacteristic",
    "PlayingOrdersSupported",
    "PlayingOrdersSupportedCharacteristic",
    "PnpIdCharacteristic",
    "PnpIdData",
    "PollenConcentrationCharacteristic",
    "PositionQualityCharacteristic",
    "PowerCharacteristic",
    "PowerSpecificationCharacteristic",
    "PreciseAcceleration3DCharacteristic",
    "PreferredUnitsCharacteristic",
    "PreferredUnitsData",
    "PressureCharacteristic",
    "PushbuttonStatus8Characteristic",
    "PushbuttonStatus8Data",
    "ButtonStatus",
    "PulseOximetryMeasurementCharacteristic",
    "RSCFeatureCharacteristic",
    "RSCMeasurementCharacteristic",
    "RainfallCharacteristic",
    "RCFeature",
    "RCFeatureCharacteristic",
    "ReconnectionAddressCharacteristic",
    "ReferenceTimeInformationCharacteristic",
    "RelativeRuntimeInACCTRangeData",
    "RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic",
    "RelativeRuntimeInACurrentRangeCharacteristic",
    "RelativeRuntimeInACurrentRangeData",
    "RelativeRuntimeInAGenericLevelRangeCharacteristic",
    "RelativeRuntimeInAGenericLevelRangeData",
    "RelativeValueInAPeriodOfDayCharacteristic",
    "RelativeValueInAPeriodOfDayData",
    "RelativeValueInATemperatureRangeCharacteristic",
    "RelativeValueInATemperatureRangeData",
    "RelativeValueInAVoltageRangeCharacteristic",
    "RelativeValueInAVoltageRangeData",
    "RelativeValueInAnIlluminanceRangeCharacteristic",
    "RelativeValueInAnIlluminanceRangeData",
    "ResolvablePrivateAddressOnlyCharacteristic",
    "RestingHeartRateCharacteristic",
    "RotationalSpeedCharacteristic",
    "RowerData",
    "RowerDataCharacteristic",
    "ScanIntervalWindowCharacteristic",
    "ScanRefreshCharacteristic",
    "SeekingSpeedCharacteristic",
    "SedentaryIntervalNotificationCharacteristic",
    "SensorLocationCharacteristic",
    "SensorLocationValue",
    "SerialNumberStringCharacteristic",
    "ServerFeatures",
    "ServerSupportedFeaturesCharacteristic",
    "ServiceChangedCharacteristic",
    "ServiceChangedData",
    "SetMemberLockCharacteristic",
    "SetMemberLockState",
    "SetMemberRankCharacteristic",
    "SoftwareRevisionStringCharacteristic",
    "SportType",
    "SportTypeForAerobicAndAnaerobicThresholdsCharacteristic",
    "StairClimberData",
    "StairClimberDataCharacteristic",
    "StepClimberData",
    "StepClimberDataCharacteristic",
    "StrideLengthCharacteristic",
    "SulfurDioxideConcentrationCharacteristic",
    "SulfurHexafluorideConcentrationCharacteristic",
    "SupportedHeartRateRangeCharacteristic",
    "SupportedHeartRateRangeData",
    "SupportedInclinationRangeCharacteristic",
    "SupportedInclinationRangeData",
    "SupportedNewAlertCategoryCharacteristic",
    "SupportedPowerRangeCharacteristic",
    "SupportedResistanceLevelRangeCharacteristic",
    "SupportedResistanceLevelRangeData",
    "SupportedSpeedRangeCharacteristic",
    "SupportedSpeedRangeData",
    "SupportedUnreadAlertCategoryCharacteristic",
    "SystemIdCharacteristic",
    "SystemIdData",
    "TemperatureCharacteristic",
    "Temperature8Characteristic",
    "Temperature8InAPeriodOfDayCharacteristic",
    "Temperature8InAPeriodOfDayData",
    "Temperature8StatisticsCharacteristic",
    "Temperature8StatisticsData",
    "TemperatureRangeCharacteristic",
    "TemperatureRangeData",
    "TemperatureStatisticsCharacteristic",
    "TemperatureStatisticsData",
    "TemperatureMeasurementCharacteristic",
    "TemperatureTypeCharacteristic",
    "TerminationReason",
    "TerminationReasonCharacteristic",
    "ThreeZoneHeartRateLimitsCharacteristic",
    "TimeAccuracyCharacteristic",
    "TimeDecihour8Characteristic",
    "TimeExponential8Characteristic",
    "TimeHour24Characteristic",
    "TimeMillisecond24Characteristic",
    "TimeSecond8Characteristic",
    "TimeSecond16Characteristic",
    "TimeSecond32Characteristic",
    "TimeSourceCharacteristic",
    "TimeUpdateControlPointCharacteristic",
    "TimeUpdateCurrentState",
    "TimeUpdateResult",
    "TimeUpdateState",
    "TimeUpdateStateCharacteristic",
    "TimeWithDstCharacteristic",
    "TimeZoneCharacteristic",
    "TMAPRole",
    "TMAPRoleCharacteristic",
    "TorqueCharacteristic",
    "TrackDurationCharacteristic",
    "TrackPositionCharacteristic",
    "TrackTitleCharacteristic",
    "TreadmillData",
    "TreadmillDataCharacteristic",
    "TrueWindDirectionCharacteristic",
    "TrueWindSpeedCharacteristic",
    "TwoZoneHeartRateLimitsCharacteristic",
    "TxPowerLevelCharacteristic",
    "UVIndexCharacteristic",
    "UncertaintyCharacteristic",
    "UnreadAlertStatusCharacteristic",
    "URICharacteristic",
    "UserIndexCharacteristic",
    "VO2MaxCharacteristic",
    "VOCConcentrationCharacteristic",
    "VoltageCharacteristic",
    "VoltageFrequencyCharacteristic",
    "VoltageSpecificationCharacteristic",
    "VoltageStatisticsCharacteristic",
    "VolumeFlags",
    "VolumeFlagsCharacteristic",
    "VolumeFlowCharacteristic",
    "WaistCircumferenceCharacteristic",
    "WeightCharacteristic",
    "WeightMeasurementCharacteristic",
    "WeightScaleFeatureCharacteristic",
    "WindChillCharacteristic",
    "get_characteristic_class_map",
]
