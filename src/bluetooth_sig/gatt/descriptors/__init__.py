"""GATT descriptors package."""

from .base import BaseDescriptor
from .cccd import CCCDData, CCCDDescriptor
from .characteristic_aggregate_format import CharacteristicAggregateFormatData, CharacteristicAggregateFormatDescriptor
from .characteristic_extended_properties import (
    CharacteristicExtendedPropertiesData,
    CharacteristicExtendedPropertiesDescriptor,
)
from .characteristic_presentation_format import (
    CharacteristicPresentationFormatData,
    CharacteristicPresentationFormatDescriptor,
)
from .characteristic_user_description import CharacteristicUserDescriptionData, CharacteristicUserDescriptionDescriptor
from .complete_br_edr_transport_block_data import (
    CompleteBREDRTransportBlockDataData,
    CompleteBREDRTransportBlockDataDescriptor,
)
from .environmental_sensing_configuration import (
    EnvironmentalSensingConfigurationData,
    EnvironmentalSensingConfigurationDescriptor,
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
from .report_reference import ReportReferenceData, ReportReferenceDescriptor
from .server_characteristic_configuration import SCCDData, ServerCharacteristicConfigurationDescriptor
from .time_trigger_setting import TimeTriggerSettingData, TimeTriggerSettingDescriptor
from .valid_range import ValidRangeData, ValidRangeDescriptor
from .valid_range_and_accuracy import ValidRangeAndAccuracyData, ValidRangeAndAccuracyDescriptor
from .value_trigger_setting import ValueTriggerSettingData, ValueTriggerSettingDescriptor

# Register built-in descriptors
DescriptorRegistry.register(CCCDDescriptor)
DescriptorRegistry.register(ValidRangeDescriptor)
DescriptorRegistry.register(CharacteristicExtendedPropertiesDescriptor)
DescriptorRegistry.register(CharacteristicUserDescriptionDescriptor)
DescriptorRegistry.register(ServerCharacteristicConfigurationDescriptor)
DescriptorRegistry.register(CharacteristicPresentationFormatDescriptor)
DescriptorRegistry.register(CharacteristicAggregateFormatDescriptor)
DescriptorRegistry.register(ExternalReportReferenceDescriptor)
DescriptorRegistry.register(ReportReferenceDescriptor)
DescriptorRegistry.register(NumberOfDigitalsDescriptor)
DescriptorRegistry.register(ValueTriggerSettingDescriptor)
DescriptorRegistry.register(EnvironmentalSensingConfigurationDescriptor)
DescriptorRegistry.register(EnvironmentalSensingMeasurementDescriptor)
DescriptorRegistry.register(EnvironmentalSensingTriggerSettingDescriptor)
DescriptorRegistry.register(TimeTriggerSettingDescriptor)
DescriptorRegistry.register(CompleteBREDRTransportBlockDataDescriptor)
DescriptorRegistry.register(ObservationScheduleDescriptor)
DescriptorRegistry.register(ValidRangeAndAccuracyDescriptor)
DescriptorRegistry.register(MeasurementDescriptionDescriptor)
DescriptorRegistry.register(ManufacturerLimitsDescriptor)
DescriptorRegistry.register(ProcessTolerancesDescriptor)
DescriptorRegistry.register(IMDTriggerSettingDescriptor)

__all__ = [
    "BaseDescriptor",
    "CCCDData",
    "CCCDDescriptor",
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
    "EnvironmentalSensingConfigurationData",
    "EnvironmentalSensingConfigurationDescriptor",
    "EnvironmentalSensingMeasurementData",
    "EnvironmentalSensingMeasurementDescriptor",
    "EnvironmentalSensingTriggerSettingData",
    "EnvironmentalSensingTriggerSettingDescriptor",
    "ExternalReportReferenceData",
    "ExternalReportReferenceDescriptor",
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
    "SCCDData",
    "ServerCharacteristicConfigurationDescriptor",
    "TimeTriggerSettingData",
    "TimeTriggerSettingDescriptor",
    "ValidRangeData",
    "ValidRangeDescriptor",
    "ValidRangeAndAccuracyData",
    "ValidRangeAndAccuracyDescriptor",
    "ValueTriggerSettingData",
    "ValueTriggerSettingDescriptor",
    "DescriptorRegistry",
]
