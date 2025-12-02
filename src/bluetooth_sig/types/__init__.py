"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from .advertising import (
    ADTypeInfo,
    AdvertisingData,
    AdvertisingDataStructures,
    BLEAdvertisingFlags,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    ConnectionData,
    CoreAdvertisingData,
    DeviceProperties,
    ExtendedAdvertisingData,
    ExtendedHeaderFlags,
    LocationAndSensingData,
    MeshAndBroadcastData,
    PDUHeaderFlags,
    PDULayout,
    PDUType,
    SecurityData,
)
from .alert import (
    ALERT_CATEGORY_DEFINED_MAX,
    ALERT_CATEGORY_RESERVED_MAX,
    ALERT_CATEGORY_RESERVED_MIN,
    ALERT_CATEGORY_SERVICE_SPECIFIC_MIN,
    ALERT_COMMAND_MAX,
    ALERT_TEXT_MAX_LENGTH,
    UNREAD_COUNT_MAX,
    UNREAD_COUNT_MORE_THAN_MAX,
    AlertCategoryBitMask,
    AlertCategoryID,
    AlertNotificationCommandID,
    validate_category_id,
)
from .appearance import AppearanceData
from .base_types import SIGInfo
from .battery import BatteryChargeLevel, BatteryChargeState, BatteryChargingType, BatteryFaultReason
from .context import CharacteristicContext, DeviceInfo
from .data_types import CharacteristicInfo, DateData, ParseFieldError, ServiceInfo, ValidationResult
from .location import PositionStatus
from .protocols import CharacteristicDataProtocol
from .registry.appearance_info import AppearanceInfo
from .registry.class_of_device import ClassOfDeviceInfo
from .registry.descriptor_types import DescriptorData, DescriptorInfo
from .units import (
    AngleUnit,
    ConcentrationUnit,
    ElectricalUnit,
    GlucoseConcentrationUnit,
    HeightUnit,
    LengthUnit,
    MeasurementSystem,
    PercentageUnit,
    PhysicalUnit,
    PressureUnit,
    SoundUnit,
    TemperatureUnit,
    WeightUnit,
)

# Device-related types are imported from device_types module to avoid cyclic imports
# Import them directly: from bluetooth_sig.types.device_types import DeviceService, DeviceEncryption

# Device-related types are imported from device_types module to avoid cyclic imports
# Import them directly: from bluetooth_sig.types.device_types import DeviceService, DeviceEncryption

__all__ = [
    "ALERT_CATEGORY_DEFINED_MAX",
    "ALERT_CATEGORY_RESERVED_MIN",
    "ALERT_CATEGORY_RESERVED_MAX",
    "ALERT_CATEGORY_SERVICE_SPECIFIC_MIN",
    "ALERT_COMMAND_MAX",
    "ALERT_TEXT_MAX_LENGTH",
    "UNREAD_COUNT_MAX",
    "UNREAD_COUNT_MORE_THAN_MAX",
    "ADTypeInfo",
    "AdvertisingData",
    "AdvertisingDataStructures",
    "AlertCategoryBitMask",
    "AlertCategoryID",
    "AlertNotificationCommandID",
    "AngleUnit",
    "AppearanceData",
    "AppearanceInfo",
    "BatteryChargeLevel",
    "BatteryChargeState",
    "BatteryChargingType",
    "BatteryFaultReason",
    "BLEAdvertisingFlags",
    "BLEAdvertisingPDU",
    "BLEExtendedHeader",
    "CharacteristicContext",
    "CharacteristicDataProtocol",
    "CharacteristicInfo",
    "ClassOfDeviceInfo",
    "ConcentrationUnit",
    "ConnectionData",
    "CoreAdvertisingData",
    "DescriptorData",
    "DescriptorInfo",
    "DateData",
    "DeviceInfo",
    "DeviceProperties",
    "ElectricalUnit",
    "ExtendedAdvertisingData",
    "ExtendedHeaderFlags",
    "GlucoseConcentrationUnit",
    "HeightUnit",
    "LengthUnit",
    "LocationAndSensingData",
    "MeasurementSystem",
    "MeshAndBroadcastData",
    "ParseFieldError",
    "PDUHeaderFlags",
    "PDULayout",
    "PDUType",
    "PercentageUnit",
    "PhysicalUnit",
    "PositionStatus",
    "PressureUnit",
    "SecurityData",
    "ServiceInfo",
    "SIGInfo",
    "SoundUnit",
    "TemperatureUnit",
    "ValidationResult",
    "WeightUnit",
    "validate_category_id",
]
