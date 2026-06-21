"""Generated type stubs for lazy package exports. Do not edit by hand."""

from .base import BaseDescriptor
from .cccd import CCCDData, CCCDDescriptor, CCCDFlags
from .characteristic_aggregate_format import CharacteristicAggregateFormatData, CharacteristicAggregateFormatDescriptor
from .characteristic_extended_properties import (
    CharacteristicExtendedPropertiesData,
    CharacteristicExtendedPropertiesDescriptor,
    ExtendedPropertiesFlags,
)
from .characteristic_presentation_format import (
    CharacteristicPresentationFormatData,
    CharacteristicPresentationFormatDescriptor,
    FormatNamespace,
    FormatType,
)
from .characteristic_user_description import CharacteristicUserDescriptionData, CharacteristicUserDescriptionDescriptor
from .complete_br_edr_transport_block_data import (
    CompleteBREDRTransportBlockDataData,
    CompleteBREDRTransportBlockDataDescriptor,
)
from .environmental_sensing_configuration import (
    EnvironmentalSensingConfigurationData,
    EnvironmentalSensingConfigurationDescriptor,
    ESCFlags,
)
from .environmental_sensing_measurement import (
    EnvironmentalSensingMeasurementData,
    EnvironmentalSensingMeasurementDescriptor,
)
from .environmental_sensing_trigger_setting import (
    EnvironmentalSensingTriggerSettingData,
    EnvironmentalSensingTriggerSettingDescriptor,
)
from .external_report_reference import ExternalReportReferenceData, ExternalReportReferenceDescriptor
from .imd_trigger_setting import IMDTriggerSettingData, IMDTriggerSettingDescriptor
from .manufacturer_limits import ManufacturerLimitsData, ManufacturerLimitsDescriptor
from .measurement_description import MeasurementDescriptionData, MeasurementDescriptionDescriptor
from .number_of_digitals import NumberOfDigitalsData, NumberOfDigitalsDescriptor
from .observation_schedule import ObservationScheduleData, ObservationScheduleDescriptor
from .process_tolerances import ProcessTolerancesData, ProcessTolerancesDescriptor
from .registry import DescriptorRegistry
from .report_reference import ReportReferenceData, ReportReferenceDescriptor, ReportType
from .server_characteristic_configuration import SCCDData, SCCDFlags, ServerCharacteristicConfigurationDescriptor
from .time_trigger_setting import TimeTriggerSettingData, TimeTriggerSettingDescriptor
from .valid_range import ValidRangeData, ValidRangeDescriptor
from .valid_range_and_accuracy import ValidRangeAndAccuracyData, ValidRangeAndAccuracyDescriptor
from .value_trigger_setting import TriggerCondition, ValueTriggerSettingData, ValueTriggerSettingDescriptor

__all__ = [
    "BaseDescriptor",
    "DescriptorRegistry",
    "CCCDData",
    "CCCDDescriptor",
    "CCCDFlags",
    "CharacteristicAggregateFormatData",
    "CharacteristicAggregateFormatDescriptor",
    "CharacteristicExtendedPropertiesData",
    "CharacteristicExtendedPropertiesDescriptor",
    "CharacteristicPresentationFormatData",
    "CharacteristicPresentationFormatDescriptor",
    "CharacteristicUserDescriptionData",
    "CharacteristicUserDescriptionDescriptor",
    "CompleteBREDRTransportBlockDataData",
    "CompleteBREDRTransportBlockDataDescriptor",
    "ESCFlags",
    "EnvironmentalSensingConfigurationData",
    "EnvironmentalSensingConfigurationDescriptor",
    "EnvironmentalSensingMeasurementData",
    "EnvironmentalSensingMeasurementDescriptor",
    "EnvironmentalSensingTriggerSettingData",
    "EnvironmentalSensingTriggerSettingDescriptor",
    "ExtendedPropertiesFlags",
    "ExternalReportReferenceData",
    "ExternalReportReferenceDescriptor",
    "FormatNamespace",
    "FormatType",
    "IMDTriggerSettingData",
    "IMDTriggerSettingDescriptor",
    "ManufacturerLimitsData",
    "ManufacturerLimitsDescriptor",
    "MeasurementDescriptionData",
    "MeasurementDescriptionDescriptor",
    "NumberOfDigitalsData",
    "NumberOfDigitalsDescriptor",
    "ObservationScheduleData",
    "ObservationScheduleDescriptor",
    "ProcessTolerancesData",
    "ProcessTolerancesDescriptor",
    "ReportReferenceData",
    "ReportReferenceDescriptor",
    "ReportType",
    "SCCDData",
    "SCCDFlags",
    "ServerCharacteristicConfigurationDescriptor",
    "TimeTriggerSettingData",
    "TimeTriggerSettingDescriptor",
    "TriggerCondition",
    "ValidRangeAndAccuracyData",
    "ValidRangeAndAccuracyDescriptor",
    "ValidRangeData",
    "ValidRangeDescriptor",
    "ValueTriggerSettingData",
    "ValueTriggerSettingDescriptor",
]
