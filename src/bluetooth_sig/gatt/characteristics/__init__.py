"""Bluetooth SIG GATT characteristic registry.

Provides type-safe, registry-driven lookup for all supported
characteristics. Now encapsulated in CharacteristicRegistry class for
API clarity and extensibility.
"""

from __future__ import annotations

from .acceleration import AccelerationCharacteristic
from .acceleration_3d import Acceleration3DCharacteristic
from .acceleration_detection_status import AccelerationDetectionStatusCharacteristic
from .acs_control_point import ACSControlPointCharacteristic
from .acs_data_in import ACSDataInCharacteristic
from .acs_data_out_indicate import ACSDataOutIndicateCharacteristic
from .acs_data_out_notify import ACSDataOutNotifyCharacteristic
from .acs_status import ACSStatusCharacteristic
from .active_preset_index import ActivePresetIndexCharacteristic
from .activity_goal import ActivityGoalCharacteristic
from .advertising_constant_tone_extension_interval import AdvertisingConstantToneExtensionIntervalCharacteristic
from .advertising_constant_tone_extension_minimum_length import (
    AdvertisingConstantToneExtensionMinimumLengthCharacteristic,
)
from .advertising_constant_tone_extension_minimum_transmit_count import (
    AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic,
)
from .advertising_constant_tone_extension_phy import AdvertisingConstantToneExtensionPhyCharacteristic
from .advertising_constant_tone_extension_transmit_duration import (
    AdvertisingConstantToneExtensionTransmitDurationCharacteristic,
)
from .aerobic_heart_rate_lower_limit import AerobicHeartRateLowerLimitCharacteristic
from .aerobic_heart_rate_upper_limit import AerobicHeartRateUpperLimitCharacteristic
from .aerobic_threshold import AerobicThresholdCharacteristic
from .age import AgeCharacteristic
from .aggregate import AggregateCharacteristic
from .alert_category_id import AlertCategoryIdCharacteristic
from .alert_category_id_bit_mask import AlertCategoryIdBitMaskCharacteristic
from .alert_level import AlertLevelCharacteristic
from .alert_notification_control_point import AlertNotificationControlPointCharacteristic
from .alert_status import AlertStatusCharacteristic
from .altitude import AltitudeCharacteristic
from .ammonia_concentration import AmmoniaConcentrationCharacteristic
from .anaerobic_heart_rate_lower_limit import AnaerobicHeartRateLowerLimitCharacteristic
from .anaerobic_heart_rate_upper_limit import AnaerobicHeartRateUpperLimitCharacteristic
from .anaerobic_threshold import AnaerobicThresholdCharacteristic
from .ap_sync_key_material import APSyncKeyMaterialCharacteristic
from .apparent_energy_32 import ApparentEnergy32Characteristic
from .apparent_power import ApparentPowerCharacteristic
from .apparent_wind_direction import ApparentWindDirectionCharacteristic
from .apparent_wind_speed import ApparentWindSpeedCharacteristic
from .appearance import AppearanceCharacteristic
from .ase_control_point import ASEControlPointCharacteristic
from .audio_input_control_point import AudioInputControlPointCharacteristic
from .audio_input_description import AudioInputDescriptionCharacteristic
from .audio_input_state import AudioInputStateCharacteristic
from .audio_input_status import AudioInputStatusCharacteristic
from .audio_input_type import AudioInputTypeCharacteristic
from .audio_location import AudioLocationCharacteristic
from .audio_output_description import AudioOutputDescriptionCharacteristic
from .available_audio_contexts import AvailableAudioContextsCharacteristic
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
from .bearer_list_current_calls import BearerListCurrentCallsCharacteristic
from .bearer_provider_name import BearerProviderNameCharacteristic
from .bearer_signal_strength import BearerSignalStrengthCharacteristic
from .bearer_signal_strength_reporting_interval import BearerSignalStrengthReportingIntervalCharacteristic
from .bearer_technology import BearerTechnologyCharacteristic
from .bearer_uci import BearerUCICharacteristic
from .bearer_uri_schemes_supported_list import BearerURISchemesCharacteristic
from .bgr_features import BGRFeaturesCharacteristic
from .bgs_features import BGSFeaturesCharacteristic
from .blood_pressure_common import BaseBloodPressureCharacteristic
from .blood_pressure_feature import BloodPressureFeatureCharacteristic
from .blood_pressure_measurement import BloodPressureMeasurementCharacteristic
from .blood_pressure_record import BloodPressureRecordCharacteristic
from .bluetooth_sig_data import BluetoothSIGDataCharacteristic
from .body_composition_feature import BodyCompositionFeatureCharacteristic
from .body_composition_measurement import BodyCompositionMeasurementCharacteristic
from .body_sensor_location import BodySensorLocationCharacteristic
from .bond_management_control_point import BondManagementControlPointCharacteristic
from .bond_management_feature import BondManagementFeatureCharacteristic
from .boolean import BooleanCharacteristic
from .boot_keyboard_input_report import BootKeyboardInputReportCharacteristic
from .boot_keyboard_output_report import BootKeyboardOutputReportCharacteristic
from .boot_mouse_input_report import BootMouseInputReportCharacteristic
from .br_edr_handover_data import BREDRHandoverDataCharacteristic
from .broadcast_audio_scan_control_point import BroadcastAudioScanControlPointCharacteristic
from .broadcast_receive_state import BroadcastReceiveStateCharacteristic
from .bss_control_point import BSSControlPointCharacteristic
from .bss_response import BSSResponseCharacteristic
from .call_control_point import CallControlPointCharacteristic
from .call_control_point_optional_opcodes import CallControlPointOptionalOpcodesCharacteristic
from .call_friendly_name import CallFriendlyNameCharacteristic
from .call_state import CallStateCharacteristic
from .caloric_intake import CaloricIntakeCharacteristic
from .carbon_monoxide_concentration import CarbonMonoxideConcentrationCharacteristic
from .cardiorespiratory_activity_instantaneous_data import CardioRespiratoryActivityInstantaneousDataCharacteristic
from .cardiorespiratory_activity_summary_data import CardioRespiratoryActivitySummaryDataCharacteristic
from .central_address_resolution import CentralAddressResolutionCharacteristic
from .cgm_feature import CGMFeatureCharacteristic
from .cgm_measurement import CGMMeasurementCharacteristic
from .cgm_session_run_time import CGMSessionRunTimeCharacteristic
from .cgm_session_start_time import CGMSessionStartTimeCharacteristic
from .cgm_specific_ops_control_point import CGMSpecificOpsControlPointCharacteristic
from .cgm_status import CGMStatusCharacteristic
from .chromatic_distance_from_planckian import ChromaticDistanceFromPlanckianCharacteristic
from .chromaticity_coordinate import ChromaticityCoordinateCharacteristic
from .chromaticity_coordinates import ChromaticityCoordinatesCharacteristic
from .chromaticity_in_cct_and_duv_values import ChromaticityInCCTAndDuvValuesCharacteristic
from .chromaticity_tolerance import ChromaticityToleranceCharacteristic
from .cie_13_3_1995_color_rendering_index import CIE133ColorRenderingIndexCharacteristic
from .client_supported_features import ClientSupportedFeaturesCharacteristic
from .co2_concentration import CO2ConcentrationCharacteristic
from .coefficient import CoefficientCharacteristic
from .constant_tone_extension_enable import ConstantToneExtensionEnableCharacteristic
from .contact_status_8 import ContactStatus8Characteristic
from .content_control_id import ContentControlIdCharacteristic
from .coordinated_set_size import CoordinatedSetSizeCharacteristic
from .correlated_color_temperature import CorrelatedColorTemperatureCharacteristic
from .cosine_of_the_angle import CosineOfTheAngleCharacteristic
from .count_16 import Count16Characteristic
from .count_24 import Count24Characteristic
from .country_code import CountryCodeCharacteristic
from .cross_trainer_data import CrossTrainerDataCharacteristic
from .csc_feature import CSCFeatureCharacteristic
from .csc_measurement import CSCMeasurementCharacteristic
from .current_group_object_id import CurrentGroupObjectIdCharacteristic
from .current_time import CurrentTimeCharacteristic
from .current_track_object_id import CurrentTrackObjectIdCharacteristic
from .current_track_segments_object_id import CurrentTrackSegmentsObjectIdCharacteristic
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
from .day_date_time import DayDateTimeCharacteristic
from .day_of_week import DayOfWeekCharacteristic
from .descriptor_value_changed import DescriptorValueChangedCharacteristic
from .device_name import DeviceNameCharacteristic
from .device_time import DeviceTimeCharacteristic
from .device_time_control_point import DeviceTimeControlPointCharacteristic
from .device_time_feature import DeviceTimeFeatureCharacteristic
from .device_time_parameters import DeviceTimeParametersCharacteristic
from .device_wearing_position import DeviceWearingPositionCharacteristic
from .dew_point import DewPointCharacteristic
from .door_window_status import DoorWindowStatusCharacteristic
from .dst_offset import DstOffsetCharacteristic
from .elapsed_time import ElapsedTimeCharacteristic
from .electric_current import ElectricCurrentCharacteristic
from .electric_current_range import ElectricCurrentRangeCharacteristic
from .electric_current_specification import ElectricCurrentSpecificationCharacteristic
from .electric_current_statistics import ElectricCurrentStatisticsCharacteristic
from .elevation import ElevationCharacteristic
from .email_address import EmailAddressCharacteristic
from .emergency_id import EmergencyIdCharacteristic
from .emergency_text import EmergencyTextCharacteristic
from .encrypted_data_key_material import EncryptedDataKeyMaterialCharacteristic
from .energy import EnergyCharacteristic
from .energy_32 import Energy32Characteristic
from .energy_in_a_period_of_day import EnergyInAPeriodOfDayCharacteristic
from .enhanced_blood_pressure_measurement import EnhancedBloodPressureMeasurementCharacteristic
from .enhanced_intermediate_cuff_pressure import EnhancedIntermediateCuffPressureCharacteristic
from .esl_address import ESLAddressCharacteristic
from .esl_control_point import ESLControlPointCharacteristic
from .esl_current_absolute_time import ESLCurrentAbsoluteTimeCharacteristic
from .esl_display_information import ESLDisplayInformationCharacteristic
from .esl_image_information import ESLImageInformationCharacteristic
from .esl_led_information import ESLLEDInformationCharacteristic
from .esl_response_key_material import ESLResponseKeyMaterialCharacteristic
from .esl_sensor_information import ESLSensorInformationCharacteristic
from .estimated_service_date import EstimatedServiceDateCharacteristic
from .event_statistics import EventStatisticsCharacteristic
from .exact_time_256 import ExactTime256Characteristic
from .fat_burn_heart_rate_lower_limit import FatBurnHeartRateLowerLimitCharacteristic
from .fat_burn_heart_rate_upper_limit import FatBurnHeartRateUpperLimitCharacteristic
from .firmware_revision_string import FirmwareRevisionStringCharacteristic
from .first_name import FirstNameCharacteristic
from .first_use_date import FirstUseDateCharacteristic
from .fitness_machine_control_point import FitnessMachineControlPointCharacteristic
from .fitness_machine_feature import FitnessMachineFeatureCharacteristic
from .fitness_machine_status import FitnessMachineStatusCharacteristic
from .five_zone_heart_rate_limits import FiveZoneHeartRateLimitsCharacteristic
from .fixed_string_8 import FixedString8Characteristic
from .fixed_string_16 import FixedString16Characteristic
from .fixed_string_24 import FixedString24Characteristic
from .fixed_string_36 import FixedString36Characteristic
from .fixed_string_64 import FixedString64Characteristic
from .floor_number import FloorNumberCharacteristic
from .force import ForceCharacteristic
from .four_zone_heart_rate_limits import FourZoneHeartRateLimitsCharacteristic
from .gain_settings_attribute import GainSettingsAttributeCharacteristic
from .gender import GenderCharacteristic
from .general_activity_instantaneous_data import GeneralActivityInstantaneousDataCharacteristic
from .general_activity_summary_data import GeneralActivitySummaryDataCharacteristic
from .generic_level import GenericLevelCharacteristic
from .ghs_control_point import GHSControlPointCharacteristic
from .global_trade_item_number import GlobalTradeItemNumberCharacteristic
from .glucose_feature import GlucoseFeatureCharacteristic
from .glucose_measurement import GlucoseMeasurementCharacteristic
from .glucose_measurement_context import GlucoseMeasurementContextCharacteristic
from .gmap_role import GMAPRoleCharacteristic
from .gust_factor import GustFactorCharacteristic
from .handedness import HandednessCharacteristic
from .hardware_revision_string import HardwareRevisionStringCharacteristic
from .health_sensor_features import HealthSensorFeaturesCharacteristic
from .hearing_aid_features import HearingAidFeaturesCharacteristic
from .hearing_aid_preset_control_point import HearingAidPresetControlPointCharacteristic
from .heart_rate_control_point import HeartRateControlPointCharacteristic
from .heart_rate_max import HeartRateMaxCharacteristic
from .heart_rate_measurement import HeartRateMeasurementCharacteristic
from .heat_index import HeatIndexCharacteristic
from .height import HeightCharacteristic
from .hid_control_point import HidControlPointCharacteristic
from .hid_information import HidInformationCharacteristic
from .hid_iso_properties import HIDISOPropertiesCharacteristic
from .high_intensity_exercise_threshold import HighIntensityExerciseThresholdCharacteristic
from .high_resolution_height import HighResolutionHeightCharacteristic
from .high_temperature import HighTemperatureCharacteristic
from .high_voltage import HighVoltageCharacteristic
from .hip_circumference import HipCircumferenceCharacteristic
from .http_control_point import HTTPControlPointCharacteristic
from .http_entity_body import HTTPEntityBodyCharacteristic
from .http_headers import HTTPHeadersCharacteristic
from .http_status_code import HTTPStatusCodeCharacteristic
from .https_security import HttpsSecurityCharacteristic
from .humidity import HumidityCharacteristic
from .humidity_8 import Humidity8Characteristic
from .idd_annunciation_status import IDDAnnunciationStatusCharacteristic
from .idd_command_control_point import IDDCommandControlPointCharacteristic
from .idd_command_data import IDDCommandDataCharacteristic
from .idd_features import IDDFeaturesCharacteristic
from .idd_history_data import IDDHistoryDataCharacteristic
from .idd_record_access_control_point import IDDRecordAccessControlPointCharacteristic
from .idd_status import IDDStatusCharacteristic
from .idd_status_changed import IDDStatusChangedCharacteristic
from .idd_status_reader_control_point import IDDStatusReaderControlPointCharacteristic
from .ieee_11073_20601_regulatory_certification_data_list import IEEE1107320601RegulatoryCharacteristic
from .illuminance import IlluminanceCharacteristic
from .illuminance_16 import Illuminance16Characteristic
from .imd_control import IMDControlCharacteristic
from .imd_historical_data import IMDHistoricalDataCharacteristic
from .imd_status import IMDStatusCharacteristic
from .imds_descriptor_value_changed import IMDSDescriptorValueChangedCharacteristic
from .incoming_call import IncomingCallCharacteristic
from .incoming_call_target_bearer_uri import IncomingCallTargetBearerURICharacteristic
from .indoor_bike_data import IndoorBikeDataCharacteristic
from .indoor_positioning_configuration import IndoorPositioningConfigurationCharacteristic
from .intermediate_cuff_pressure import IntermediateCuffPressureCharacteristic
from .intermediate_temperature import IntermediateTemperatureCharacteristic
from .irradiance import IrradianceCharacteristic
from .language import LanguageCharacteristic
from .last_name import LastNameCharacteristic
from .latitude import LatitudeCharacteristic
from .le_gatt_security_levels import LEGATTSecurityLevelsCharacteristic
from .le_hid_operation_mode import LEHIDOperationModeCharacteristic
from .length import LengthCharacteristic
from .life_cycle_data import LifeCycleDataCharacteristic
from .light_distribution import LightDistributionCharacteristic
from .light_output import LightOutputCharacteristic
from .light_source_type import LightSourceTypeCharacteristic
from .linear_position import LinearPositionCharacteristic
from .live_health_observations import LiveHealthObservationsCharacteristic
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
from .luminous_flux_range import LuminousFluxRangeCharacteristic
from .luminous_intensity import LuminousIntensityCharacteristic
from .magnetic_declination import MagneticDeclinationCharacteristic
from .magnetic_flux_density_2d import MagneticFluxDensity2DCharacteristic
from .magnetic_flux_density_3d import MagneticFluxDensity3DCharacteristic
from .manufacturer_name_string import ManufacturerNameStringCharacteristic
from .mass_flow import MassFlowCharacteristic
from .maximum_recommended_heart_rate import MaximumRecommendedHeartRateCharacteristic
from .measurement_interval import MeasurementIntervalCharacteristic
from .media_control_point import MediaControlPointCharacteristic
from .media_control_point_opcodes_supported import MediaControlPointOpcodesSupportedCharacteristic
from .media_player_icon_object_id import MediaPlayerIconObjectIdCharacteristic
from .media_player_icon_url import MediaPlayerIconURLCharacteristic
from .media_player_name import MediaPlayerNameCharacteristic
from .media_state import MediaStateCharacteristic
from .mesh_provisioning_data_in import MeshProvisioningDataInCharacteristic
from .mesh_provisioning_data_out import MeshProvisioningDataOutCharacteristic
from .mesh_proxy_data_in import MeshProxyDataInCharacteristic
from .mesh_proxy_data_out import MeshProxyDataOutCharacteristic
from .methane_concentration import MethaneConcentrationCharacteristic
from .middle_name import MiddleNameCharacteristic
from .model_number_string import ModelNumberStringCharacteristic
from .mute import MuteCharacteristic
from .navigation import NavigationCharacteristic
from .new_alert import NewAlertCharacteristic
from .next_track_object_id import NextTrackObjectIdCharacteristic
from .nitrogen_dioxide_concentration import NitrogenDioxideConcentrationCharacteristic
from .noise import NoiseCharacteristic
from .non_methane_voc_concentration import NonMethaneVOCConcentrationCharacteristic
from .object_action_control_point import ObjectActionControlPointCharacteristic
from .object_changed import ObjectChangedCharacteristic
from .object_first_created import ObjectFirstCreatedCharacteristic
from .object_id import ObjectIdCharacteristic
from .object_last_modified import ObjectLastModifiedCharacteristic
from .object_list_control_point import ObjectListControlPointCharacteristic
from .object_list_filter import ObjectListFilterCharacteristic
from .object_name import ObjectNameCharacteristic
from .object_properties import ObjectPropertiesCharacteristic
from .object_size import ObjectSizeCharacteristic
from .object_type import ObjectTypeCharacteristic
from .observation_schedule_changed import ObservationScheduleChangedCharacteristic
from .on_demand_ranging_data import OnDemandRangingDataCharacteristic
from .ots_feature import OTSFeatureCharacteristic
from .ozone_concentration import OzoneConcentrationCharacteristic
from .parent_group_object_id import ParentGroupObjectIdCharacteristic
from .perceived_lightness import PerceivedLightnessCharacteristic
from .percentage_8 import Percentage8Characteristic
from .percentage_8_steps import Percentage8StepsCharacteristic
from .peripheral_preferred_connection_parameters import PeripheralPreferredConnectionParametersCharacteristic
from .peripheral_privacy_flag import PeripheralPrivacyFlagCharacteristic
from .physical_activity_current_session import PhysicalActivityCurrentSessionCharacteristic
from .physical_activity_monitor_control_point import PhysicalActivityMonitorControlPointCharacteristic
from .physical_activity_monitor_features import PhysicalActivityMonitorFeaturesCharacteristic
from .physical_activity_session_descriptor import PhysicalActivitySessionDescriptorCharacteristic
from .playback_speed import PlaybackSpeedCharacteristic
from .playing_order import PlayingOrderCharacteristic
from .playing_orders_supported import PlayingOrdersSupportedCharacteristic
from .plx_features import PLXFeaturesCharacteristic
from .plx_spot_check_measurement import PLXSpotCheckMeasurementCharacteristic
from .pm1_concentration import PM1ConcentrationCharacteristic
from .pm10_concentration import PM10ConcentrationCharacteristic
from .pm25_concentration import PM25ConcentrationCharacteristic
from .pnp_id import PnpIdCharacteristic
from .pollen_concentration import PollenConcentrationCharacteristic
from .position_quality import PositionQualityCharacteristic
from .power import PowerCharacteristic
from .power_specification import PowerSpecificationCharacteristic
from .precise_acceleration_3d import PreciseAcceleration3DCharacteristic
from .preferred_units import PreferredUnitsCharacteristic
from .pressure import PressureCharacteristic
from .protocol_mode import ProtocolModeCharacteristic
from .pushbutton_status_8 import PushbuttonStatus8Characteristic
from .rainfall import RainfallCharacteristic
from .ranging_data_overwritten import RangingDataOverwrittenCharacteristic
from .ranging_data_ready import RangingDataReadyCharacteristic
from .ras_control_point import RASControlPointCharacteristic
from .ras_features import RASFeaturesCharacteristic
from .rc_feature import RCFeatureCharacteristic
from .rc_settings import RCSettingsCharacteristic
from .real_time_ranging_data import RealTimeRangingDataCharacteristic
from .reconnection_address import ReconnectionAddressCharacteristic
from .reconnection_configuration_control_point import ReconnectionConfigurationControlPointCharacteristic
from .record_access_control_point import RecordAccessControlPointCharacteristic
from .reference_time_information import ReferenceTimeInformationCharacteristic
from .registered_user import RegisteredUserCharacteristic
from .registry import CharacteristicName, CharacteristicRegistry, get_characteristic_class_map
from .relative_runtime_in_a_correlated_color_temperature_range import (
    RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic,
)
from .relative_runtime_in_a_current_range import RelativeRuntimeInACurrentRangeCharacteristic
from .relative_runtime_in_a_generic_level_range import RelativeRuntimeInAGenericLevelRangeCharacteristic
from .relative_value_in_a_period_of_day import RelativeValueInAPeriodOfDayCharacteristic
from .relative_value_in_a_temperature_range import RelativeValueInATemperatureRangeCharacteristic
from .relative_value_in_a_voltage_range import RelativeValueInAVoltageRangeCharacteristic
from .relative_value_in_an_illuminance_range import RelativeValueInAnIlluminanceRangeCharacteristic
from .report import ReportCharacteristic
from .report_map import ReportMapCharacteristic
from .resolvable_private_address_only import ResolvablePrivateAddressOnlyCharacteristic
from .resting_heart_rate import RestingHeartRateCharacteristic
from .ringer_control_point import RingerControlPointCharacteristic
from .ringer_setting import RingerSettingCharacteristic
from .rotational_speed import RotationalSpeedCharacteristic
from .rower_data import RowerDataCharacteristic
from .rsc_feature import RSCFeatureCharacteristic
from .rsc_measurement import RSCMeasurementCharacteristic
from .sc_control_point import SCControlPointCharacteristic
from .scan_interval_window import ScanIntervalWindowCharacteristic
from .scan_refresh import ScanRefreshCharacteristic
from .search_control_point import SearchControlPointCharacteristic
from .search_results_object_id import SearchResultsObjectIdCharacteristic
from .sedentary_interval_notification import SedentaryIntervalNotificationCharacteristic
from .seeking_speed import SeekingSpeedCharacteristic
from .sensor_location import SensorLocationCharacteristic
from .serial_number_string import SerialNumberStringCharacteristic
from .server_supported_features import ServerSupportedFeaturesCharacteristic
from .service_changed import ServiceChangedCharacteristic
from .service_cycle_data import ServiceCycleDataCharacteristic
from .set_identity_resolving_key import SetIdentityResolvingKeyCharacteristic
from .set_member_lock import SetMemberLockCharacteristic
from .set_member_rank import SetMemberRankCharacteristic
from .sink_ase import SinkASECharacteristic
from .sink_audio_locations import SinkAudioLocationsCharacteristic
from .sink_pac import SinkPACCharacteristic
from .sleep_activity_instantaneous_data import SleepActivityInstantaneousDataCharacteristic
from .sleep_activity_summary_data import SleepActivitySummaryDataCharacteristic
from .software_revision_string import SoftwareRevisionStringCharacteristic
from .source_ase import SourceASECharacteristic
from .source_audio_locations import SourceAudioLocationsCharacteristic
from .source_pac import SourcePACCharacteristic
from .sport_type_for_aerobic_and_anaerobic_thresholds import SportTypeForAerobicAndAnaerobicThresholdsCharacteristic
from .stair_climber_data import StairClimberDataCharacteristic
from .status_flags import StatusFlagsCharacteristic
from .step_climber_data import StepClimberDataCharacteristic
from .step_counter_activity_summary_data import StepCounterActivitySummaryDataCharacteristic
from .stored_health_observations import StoredHealthObservationsCharacteristic
from .stride_length import StrideLengthCharacteristic
from .sulfur_dioxide_concentration import SulfurDioxideConcentrationCharacteristic
from .sulfur_hexafluoride_concentration import SulfurHexafluorideConcentrationCharacteristic
from .supported_audio_contexts import SupportedAudioContextsCharacteristic
from .supported_heart_rate_range import SupportedHeartRateRangeCharacteristic
from .supported_inclination_range import SupportedInclinationRangeCharacteristic
from .supported_new_alert_category import SupportedNewAlertCategoryCharacteristic
from .supported_power_range import SupportedPowerRangeCharacteristic
from .supported_resistance_level_range import SupportedResistanceLevelRangeCharacteristic
from .supported_speed_range import SupportedSpeedRangeCharacteristic
from .supported_unread_alert_category import SupportedUnreadAlertCategoryCharacteristic
from .system_id import SystemIdCharacteristic
from .tds_control_point import TDSControlPointCharacteristic
from .temperature import TemperatureCharacteristic
from .temperature_8 import Temperature8Characteristic
from .temperature_8_in_a_period_of_day import Temperature8InAPeriodOfDayCharacteristic
from .temperature_8_statistics import Temperature8StatisticsCharacteristic
from .temperature_measurement import TemperatureMeasurementCharacteristic
from .temperature_range import TemperatureRangeCharacteristic
from .temperature_statistics import TemperatureStatisticsCharacteristic
from .temperature_type import TemperatureTypeCharacteristic
from .termination_reason import TerminationReasonCharacteristic
from .three_zone_heart_rate_limits import ThreeZoneHeartRateLimitsCharacteristic
from .time_accuracy import TimeAccuracyCharacteristic
from .time_change_log_data import TimeChangeLogDataCharacteristic
from .time_decihour_8 import TimeDecihour8Characteristic
from .time_exponential_8 import TimeExponential8Characteristic
from .time_hour_24 import TimeHour24Characteristic
from .time_millisecond_24 import TimeMillisecond24Characteristic
from .time_second_8 import TimeSecond8Characteristic
from .time_second_16 import TimeSecond16Characteristic
from .time_second_32 import TimeSecond32Characteristic
from .time_source import TimeSourceCharacteristic
from .time_update_control_point import TimeUpdateControlPointCharacteristic
from .time_update_state import TimeUpdateStateCharacteristic
from .time_with_dst import TimeWithDstCharacteristic
from .time_zone import TimeZoneCharacteristic
from .tmap_role import TMAPRoleCharacteristic
from .torque import TorqueCharacteristic
from .track_changed import TrackChangedCharacteristic
from .track_duration import TrackDurationCharacteristic
from .track_position import TrackPositionCharacteristic
from .track_title import TrackTitleCharacteristic
from .training_status import TrainingStatusCharacteristic
from .treadmill_data import TreadmillDataCharacteristic
from .true_wind_direction import TrueWindDirectionCharacteristic
from .true_wind_speed import TrueWindSpeedCharacteristic
from .two_zone_heart_rate_limits import TwoZoneHeartRateLimitsCharacteristic
from .tx_power_level import TxPowerLevelCharacteristic
from .udi_for_medical_devices import UDIForMedicalDevicesCharacteristic
from .ugg_features import UGGFeaturesCharacteristic
from .ugt_features import UGTFeaturesCharacteristic
from .uncertainty import UncertaintyCharacteristic
from .unknown import UnknownCharacteristic
from .unread_alert_status import UnreadAlertStatusCharacteristic
from .uri import URICharacteristic
from .user_control_point import UserControlPointCharacteristic
from .user_index import UserIndexCharacteristic
from .uv_index import UVIndexCharacteristic
from .vo2_max import VO2MaxCharacteristic
from .voc_concentration import VOCConcentrationCharacteristic
from .voltage import VoltageCharacteristic
from .voltage_frequency import VoltageFrequencyCharacteristic
from .voltage_specification import VoltageSpecificationCharacteristic
from .voltage_statistics import VoltageStatisticsCharacteristic
from .volume_control_point import VolumeControlPointCharacteristic
from .volume_flags import VolumeFlagsCharacteristic
from .volume_flow import VolumeFlowCharacteristic
from .volume_offset_control_point import VolumeOffsetControlPointCharacteristic
from .volume_offset_state import VolumeOffsetStateCharacteristic
from .volume_state import VolumeStateCharacteristic
from .waist_circumference import WaistCircumferenceCharacteristic
from .weight import WeightCharacteristic
from .weight_measurement import WeightMeasurementCharacteristic
from .weight_scale_feature import WeightScaleFeatureCharacteristic
from .wind_chill import WindChillCharacteristic
from .work_cycle_data import WorkCycleDataCharacteristic

__all__ = [
    "BaseCharacteristic",
    "CharacteristicName",
    "CharacteristicRegistry",
    "get_characteristic_class_map",
    "AccelerationCharacteristic",
    "Acceleration3DCharacteristic",
    "AccelerationDetectionStatusCharacteristic",
    "ACSControlPointCharacteristic",
    "ACSDataInCharacteristic",
    "ACSDataOutIndicateCharacteristic",
    "ACSDataOutNotifyCharacteristic",
    "ACSStatusCharacteristic",
    "ActivePresetIndexCharacteristic",
    "ActivityGoalCharacteristic",
    "AdvertisingConstantToneExtensionIntervalCharacteristic",
    "AdvertisingConstantToneExtensionMinimumLengthCharacteristic",
    "AdvertisingConstantToneExtensionMinimumTransmitCountCharacteristic",
    "AdvertisingConstantToneExtensionPhyCharacteristic",
    "AdvertisingConstantToneExtensionTransmitDurationCharacteristic",
    "AerobicHeartRateLowerLimitCharacteristic",
    "AerobicHeartRateUpperLimitCharacteristic",
    "AerobicThresholdCharacteristic",
    "AgeCharacteristic",
    "AggregateCharacteristic",
    "AlertCategoryIdCharacteristic",
    "AlertCategoryIdBitMaskCharacteristic",
    "AlertLevelCharacteristic",
    "AlertNotificationControlPointCharacteristic",
    "AlertStatusCharacteristic",
    "AltitudeCharacteristic",
    "AmmoniaConcentrationCharacteristic",
    "AnaerobicHeartRateLowerLimitCharacteristic",
    "AnaerobicHeartRateUpperLimitCharacteristic",
    "AnaerobicThresholdCharacteristic",
    "APSyncKeyMaterialCharacteristic",
    "ApparentEnergy32Characteristic",
    "ApparentPowerCharacteristic",
    "ApparentWindDirectionCharacteristic",
    "ApparentWindSpeedCharacteristic",
    "AppearanceCharacteristic",
    "ASEControlPointCharacteristic",
    "AudioInputControlPointCharacteristic",
    "AudioInputDescriptionCharacteristic",
    "AudioInputStateCharacteristic",
    "AudioInputStatusCharacteristic",
    "AudioInputTypeCharacteristic",
    "AudioLocationCharacteristic",
    "AudioOutputDescriptionCharacteristic",
    "AvailableAudioContextsCharacteristic",
    "AverageCurrentCharacteristic",
    "AverageVoltageCharacteristic",
    "BarometricPressureTrendCharacteristic",
    "BatteryCriticalStatusCharacteristic",
    "BatteryEnergyStatusCharacteristic",
    "BatteryHealthInformationCharacteristic",
    "BatteryHealthStatusCharacteristic",
    "BatteryInformationCharacteristic",
    "BatteryLevelCharacteristic",
    "BatteryLevelStatusCharacteristic",
    "BatteryTimeStatusCharacteristic",
    "BearerListCurrentCallsCharacteristic",
    "BearerProviderNameCharacteristic",
    "BearerSignalStrengthCharacteristic",
    "BearerSignalStrengthReportingIntervalCharacteristic",
    "BearerTechnologyCharacteristic",
    "BearerUCICharacteristic",
    "BearerURISchemesCharacteristic",
    "BGRFeaturesCharacteristic",
    "BGSFeaturesCharacteristic",
    "BaseBloodPressureCharacteristic",
    "BloodPressureFeatureCharacteristic",
    "BloodPressureMeasurementCharacteristic",
    "BloodPressureRecordCharacteristic",
    "BluetoothSIGDataCharacteristic",
    "BodyCompositionFeatureCharacteristic",
    "BodyCompositionMeasurementCharacteristic",
    "BodySensorLocationCharacteristic",
    "BondManagementControlPointCharacteristic",
    "BondManagementFeatureCharacteristic",
    "BooleanCharacteristic",
    "BootKeyboardInputReportCharacteristic",
    "BootKeyboardOutputReportCharacteristic",
    "BootMouseInputReportCharacteristic",
    "BREDRHandoverDataCharacteristic",
    "BroadcastAudioScanControlPointCharacteristic",
    "BroadcastReceiveStateCharacteristic",
    "BSSControlPointCharacteristic",
    "BSSResponseCharacteristic",
    "CallControlPointCharacteristic",
    "CallControlPointOptionalOpcodesCharacteristic",
    "CallFriendlyNameCharacteristic",
    "CallStateCharacteristic",
    "CaloricIntakeCharacteristic",
    "CarbonMonoxideConcentrationCharacteristic",
    "CardioRespiratoryActivityInstantaneousDataCharacteristic",
    "CardioRespiratoryActivitySummaryDataCharacteristic",
    "CentralAddressResolutionCharacteristic",
    "CGMFeatureCharacteristic",
    "CGMMeasurementCharacteristic",
    "CGMSessionRunTimeCharacteristic",
    "CGMSessionStartTimeCharacteristic",
    "CGMSpecificOpsControlPointCharacteristic",
    "CGMStatusCharacteristic",
    "ChromaticDistanceFromPlanckianCharacteristic",
    "ChromaticityCoordinateCharacteristic",
    "ChromaticityCoordinatesCharacteristic",
    "ChromaticityInCCTAndDuvValuesCharacteristic",
    "ChromaticityToleranceCharacteristic",
    "CIE133ColorRenderingIndexCharacteristic",
    "ClientSupportedFeaturesCharacteristic",
    "CO2ConcentrationCharacteristic",
    "CoefficientCharacteristic",
    "ConstantToneExtensionEnableCharacteristic",
    "ContactStatus8Characteristic",
    "ContentControlIdCharacteristic",
    "CoordinatedSetSizeCharacteristic",
    "CorrelatedColorTemperatureCharacteristic",
    "CosineOfTheAngleCharacteristic",
    "Count16Characteristic",
    "Count24Characteristic",
    "CountryCodeCharacteristic",
    "CrossTrainerDataCharacteristic",
    "CSCFeatureCharacteristic",
    "CSCMeasurementCharacteristic",
    "ElapsedTimeCharacteristic",
    "CurrentGroupObjectIdCharacteristic",
    "CurrentTimeCharacteristic",
    "CurrentTrackObjectIdCharacteristic",
    "CurrentTrackSegmentsObjectIdCharacteristic",
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
    "DayOfWeekCharacteristic",
    "DescriptorValueChangedCharacteristic",
    "DeviceNameCharacteristic",
    "DeviceTimeCharacteristic",
    "DeviceTimeControlPointCharacteristic",
    "DeviceTimeFeatureCharacteristic",
    "DeviceTimeParametersCharacteristic",
    "DeviceWearingPositionCharacteristic",
    "DewPointCharacteristic",
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
    "EncryptedDataKeyMaterialCharacteristic",
    "EnergyCharacteristic",
    "Energy32Characteristic",
    "EnergyInAPeriodOfDayCharacteristic",
    "EnhancedBloodPressureMeasurementCharacteristic",
    "EnhancedIntermediateCuffPressureCharacteristic",
    "ESLAddressCharacteristic",
    "ESLControlPointCharacteristic",
    "ESLCurrentAbsoluteTimeCharacteristic",
    "ESLDisplayInformationCharacteristic",
    "ESLImageInformationCharacteristic",
    "ESLLEDInformationCharacteristic",
    "ESLResponseKeyMaterialCharacteristic",
    "ESLSensorInformationCharacteristic",
    "EstimatedServiceDateCharacteristic",
    "EventStatisticsCharacteristic",
    "ExactTime256Characteristic",
    "FatBurnHeartRateLowerLimitCharacteristic",
    "FatBurnHeartRateUpperLimitCharacteristic",
    "FirmwareRevisionStringCharacteristic",
    "FirstNameCharacteristic",
    "FirstUseDateCharacteristic",
    "FitnessMachineControlPointCharacteristic",
    "FitnessMachineFeatureCharacteristic",
    "FitnessMachineStatusCharacteristic",
    "FiveZoneHeartRateLimitsCharacteristic",
    "FixedString16Characteristic",
    "FixedString24Characteristic",
    "FixedString36Characteristic",
    "FixedString64Characteristic",
    "FixedString8Characteristic",
    "FloorNumberCharacteristic",
    "ForceCharacteristic",
    "FourZoneHeartRateLimitsCharacteristic",
    "GainSettingsAttributeCharacteristic",
    "GenderCharacteristic",
    "GeneralActivityInstantaneousDataCharacteristic",
    "GeneralActivitySummaryDataCharacteristic",
    "GenericLevelCharacteristic",
    "GHSControlPointCharacteristic",
    "GlobalTradeItemNumberCharacteristic",
    "GlucoseFeatureCharacteristic",
    "GlucoseMeasurementCharacteristic",
    "GlucoseMeasurementContextCharacteristic",
    "GMAPRoleCharacteristic",
    "GustFactorCharacteristic",
    "HandednessCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "HealthSensorFeaturesCharacteristic",
    "HearingAidFeaturesCharacteristic",
    "HearingAidPresetControlPointCharacteristic",
    "HeartRateControlPointCharacteristic",
    "HeartRateMaxCharacteristic",
    "HeartRateMeasurementCharacteristic",
    "HeatIndexCharacteristic",
    "HeightCharacteristic",
    "HidControlPointCharacteristic",
    "HidInformationCharacteristic",
    "HIDISOPropertiesCharacteristic",
    "HighIntensityExerciseThresholdCharacteristic",
    "HighResolutionHeightCharacteristic",
    "HighTemperatureCharacteristic",
    "HighVoltageCharacteristic",
    "HipCircumferenceCharacteristic",
    "HTTPControlPointCharacteristic",
    "HTTPEntityBodyCharacteristic",
    "HTTPHeadersCharacteristic",
    "HTTPStatusCodeCharacteristic",
    "HttpsSecurityCharacteristic",
    "HumidityCharacteristic",
    "Humidity8Characteristic",
    "IDDAnnunciationStatusCharacteristic",
    "IDDCommandControlPointCharacteristic",
    "IDDCommandDataCharacteristic",
    "IDDFeaturesCharacteristic",
    "IDDHistoryDataCharacteristic",
    "IDDRecordAccessControlPointCharacteristic",
    "IDDStatusCharacteristic",
    "IDDStatusChangedCharacteristic",
    "IDDStatusReaderControlPointCharacteristic",
    "IEEE1107320601RegulatoryCharacteristic",
    "IlluminanceCharacteristic",
    "Illuminance16Characteristic",
    "IMDControlCharacteristic",
    "IMDHistoricalDataCharacteristic",
    "IMDStatusCharacteristic",
    "IMDSDescriptorValueChangedCharacteristic",
    "IncomingCallCharacteristic",
    "IncomingCallTargetBearerURICharacteristic",
    "IndoorBikeDataCharacteristic",
    "IndoorPositioningConfigurationCharacteristic",
    "IntermediateCuffPressureCharacteristic",
    "IntermediateTemperatureCharacteristic",
    "IrradianceCharacteristic",
    "LanguageCharacteristic",
    "LastNameCharacteristic",
    "LatitudeCharacteristic",
    "LEGATTSecurityLevelsCharacteristic",
    "LEHIDOperationModeCharacteristic",
    "LengthCharacteristic",
    "LifeCycleDataCharacteristic",
    "LightDistributionCharacteristic",
    "LightOutputCharacteristic",
    "LightSourceTypeCharacteristic",
    "LinearPositionCharacteristic",
    "LiveHealthObservationsCharacteristic",
    "LNControlPointCharacteristic",
    "LNFeatureCharacteristic",
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
    "LuminousIntensityCharacteristic",
    "MagneticDeclinationCharacteristic",
    "MagneticFluxDensity2DCharacteristic",
    "MagneticFluxDensity3DCharacteristic",
    "ManufacturerNameStringCharacteristic",
    "MassFlowCharacteristic",
    "MaximumRecommendedHeartRateCharacteristic",
    "MeasurementIntervalCharacteristic",
    "MediaControlPointCharacteristic",
    "MediaControlPointOpcodesSupportedCharacteristic",
    "MediaPlayerIconObjectIdCharacteristic",
    "MediaPlayerIconURLCharacteristic",
    "MediaPlayerNameCharacteristic",
    "MediaStateCharacteristic",
    "MeshProvisioningDataInCharacteristic",
    "MeshProvisioningDataOutCharacteristic",
    "MeshProxyDataInCharacteristic",
    "MeshProxyDataOutCharacteristic",
    "MethaneConcentrationCharacteristic",
    "MiddleNameCharacteristic",
    "ModelNumberStringCharacteristic",
    "MuteCharacteristic",
    "NavigationCharacteristic",
    "NewAlertCharacteristic",
    "NextTrackObjectIdCharacteristic",
    "NitrogenDioxideConcentrationCharacteristic",
    "NoiseCharacteristic",
    "NonMethaneVOCConcentrationCharacteristic",
    "ObjectActionControlPointCharacteristic",
    "ObjectChangedCharacteristic",
    "ObjectFirstCreatedCharacteristic",
    "ObjectIdCharacteristic",
    "ObjectLastModifiedCharacteristic",
    "ObjectListControlPointCharacteristic",
    "ObjectListFilterCharacteristic",
    "ObjectNameCharacteristic",
    "ObjectPropertiesCharacteristic",
    "ObjectSizeCharacteristic",
    "ObjectTypeCharacteristic",
    "ObservationScheduleChangedCharacteristic",
    "OnDemandRangingDataCharacteristic",
    "OTSFeatureCharacteristic",
    "OzoneConcentrationCharacteristic",
    "ParentGroupObjectIdCharacteristic",
    "PerceivedLightnessCharacteristic",
    "Percentage8Characteristic",
    "Percentage8StepsCharacteristic",
    "PeripheralPreferredConnectionParametersCharacteristic",
    "PeripheralPrivacyFlagCharacteristic",
    "PhysicalActivityCurrentSessionCharacteristic",
    "PhysicalActivityMonitorControlPointCharacteristic",
    "PhysicalActivityMonitorFeaturesCharacteristic",
    "PhysicalActivitySessionDescriptorCharacteristic",
    "PlaybackSpeedCharacteristic",
    "PlayingOrderCharacteristic",
    "PlayingOrdersSupportedCharacteristic",
    "PLXFeaturesCharacteristic",
    "PLXSpotCheckMeasurementCharacteristic",
    "PM10ConcentrationCharacteristic",
    "PM1ConcentrationCharacteristic",
    "PM25ConcentrationCharacteristic",
    "PnpIdCharacteristic",
    "PollenConcentrationCharacteristic",
    "PositionQualityCharacteristic",
    "PowerCharacteristic",
    "PowerSpecificationCharacteristic",
    "PreciseAcceleration3DCharacteristic",
    "PreferredUnitsCharacteristic",
    "PressureCharacteristic",
    "ProtocolModeCharacteristic",
    "PushbuttonStatus8Characteristic",
    "RainfallCharacteristic",
    "RangingDataOverwrittenCharacteristic",
    "RangingDataReadyCharacteristic",
    "RASControlPointCharacteristic",
    "RASFeaturesCharacteristic",
    "RCFeatureCharacteristic",
    "RCSettingsCharacteristic",
    "RealTimeRangingDataCharacteristic",
    "ReconnectionAddressCharacteristic",
    "ReconnectionConfigurationControlPointCharacteristic",
    "RecordAccessControlPointCharacteristic",
    "ReferenceTimeInformationCharacteristic",
    "RegisteredUserCharacteristic",
    "RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic",
    "RelativeRuntimeInACurrentRangeCharacteristic",
    "RelativeRuntimeInAGenericLevelRangeCharacteristic",
    "RelativeValueInAPeriodOfDayCharacteristic",
    "RelativeValueInATemperatureRangeCharacteristic",
    "RelativeValueInAVoltageRangeCharacteristic",
    "RelativeValueInAnIlluminanceRangeCharacteristic",
    "ReportCharacteristic",
    "ReportMapCharacteristic",
    "ResolvablePrivateAddressOnlyCharacteristic",
    "RestingHeartRateCharacteristic",
    "RingerControlPointCharacteristic",
    "RingerSettingCharacteristic",
    "RotationalSpeedCharacteristic",
    "RowerDataCharacteristic",
    "RSCFeatureCharacteristic",
    "RSCMeasurementCharacteristic",
    "SCControlPointCharacteristic",
    "ScanIntervalWindowCharacteristic",
    "ScanRefreshCharacteristic",
    "SearchControlPointCharacteristic",
    "SearchResultsObjectIdCharacteristic",
    "SedentaryIntervalNotificationCharacteristic",
    "SeekingSpeedCharacteristic",
    "SensorLocationCharacteristic",
    "SerialNumberStringCharacteristic",
    "ServerSupportedFeaturesCharacteristic",
    "ServiceChangedCharacteristic",
    "ServiceCycleDataCharacteristic",
    "SetIdentityResolvingKeyCharacteristic",
    "SetMemberLockCharacteristic",
    "SetMemberRankCharacteristic",
    "SinkASECharacteristic",
    "SinkAudioLocationsCharacteristic",
    "SinkPACCharacteristic",
    "SleepActivityInstantaneousDataCharacteristic",
    "SleepActivitySummaryDataCharacteristic",
    "SoftwareRevisionStringCharacteristic",
    "SourceASECharacteristic",
    "SourceAudioLocationsCharacteristic",
    "SourcePACCharacteristic",
    "SportTypeForAerobicAndAnaerobicThresholdsCharacteristic",
    "StairClimberDataCharacteristic",
    "StatusFlagsCharacteristic",
    "StepClimberDataCharacteristic",
    "StepCounterActivitySummaryDataCharacteristic",
    "StoredHealthObservationsCharacteristic",
    "StrideLengthCharacteristic",
    "SulfurDioxideConcentrationCharacteristic",
    "SulfurHexafluorideConcentrationCharacteristic",
    "SupportedAudioContextsCharacteristic",
    "SupportedHeartRateRangeCharacteristic",
    "SupportedInclinationRangeCharacteristic",
    "SupportedNewAlertCategoryCharacteristic",
    "SupportedPowerRangeCharacteristic",
    "SupportedResistanceLevelRangeCharacteristic",
    "SupportedSpeedRangeCharacteristic",
    "SupportedUnreadAlertCategoryCharacteristic",
    "SystemIdCharacteristic",
    "TDSControlPointCharacteristic",
    "TemperatureCharacteristic",
    "Temperature8Characteristic",
    "Temperature8InAPeriodOfDayCharacteristic",
    "Temperature8StatisticsCharacteristic",
    "TemperatureMeasurementCharacteristic",
    "TemperatureRangeCharacteristic",
    "TemperatureStatisticsCharacteristic",
    "TemperatureTypeCharacteristic",
    "TerminationReasonCharacteristic",
    "ThreeZoneHeartRateLimitsCharacteristic",
    "TimeAccuracyCharacteristic",
    "TimeChangeLogDataCharacteristic",
    "TimeDecihour8Characteristic",
    "TimeExponential8Characteristic",
    "TimeHour24Characteristic",
    "TimeMillisecond24Characteristic",
    "TimeSecond16Characteristic",
    "TimeSecond32Characteristic",
    "TimeSecond8Characteristic",
    "TimeSourceCharacteristic",
    "TimeUpdateControlPointCharacteristic",
    "TimeUpdateStateCharacteristic",
    "TimeWithDstCharacteristic",
    "TimeZoneCharacteristic",
    "TMAPRoleCharacteristic",
    "TorqueCharacteristic",
    "TrackChangedCharacteristic",
    "TrackDurationCharacteristic",
    "TrackPositionCharacteristic",
    "TrackTitleCharacteristic",
    "TrainingStatusCharacteristic",
    "TreadmillDataCharacteristic",
    "TrueWindDirectionCharacteristic",
    "TrueWindSpeedCharacteristic",
    "TwoZoneHeartRateLimitsCharacteristic",
    "TxPowerLevelCharacteristic",
    "UDIForMedicalDevicesCharacteristic",
    "UGGFeaturesCharacteristic",
    "UGTFeaturesCharacteristic",
    "UncertaintyCharacteristic",
    "UnknownCharacteristic",
    "UnreadAlertStatusCharacteristic",
    "URICharacteristic",
    "UserControlPointCharacteristic",
    "UserIndexCharacteristic",
    "UVIndexCharacteristic",
    "VO2MaxCharacteristic",
    "VOCConcentrationCharacteristic",
    "VoltageCharacteristic",
    "VoltageFrequencyCharacteristic",
    "VoltageSpecificationCharacteristic",
    "VoltageStatisticsCharacteristic",
    "VolumeControlPointCharacteristic",
    "VolumeFlagsCharacteristic",
    "VolumeFlowCharacteristic",
    "VolumeOffsetControlPointCharacteristic",
    "VolumeOffsetStateCharacteristic",
    "VolumeStateCharacteristic",
    "WaistCircumferenceCharacteristic",
    "WeightCharacteristic",
    "WeightMeasurementCharacteristic",
    "WeightScaleFeatureCharacteristic",
    "WindChillCharacteristic",
    "WorkCycleDataCharacteristic",
]
