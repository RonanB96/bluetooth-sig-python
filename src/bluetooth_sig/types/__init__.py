"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from .advertising import (
    AdvertisementData,
    AdvertisingData,
    AdvertisingDataStructures,
    BLEAdvertisingFlags,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    CoreAdvertisingData,
    DeviceProperties,
    DirectedAdvertisingData,
    ExtendedAdvertisingData,
    ExtendedHeaderFlags,
    LocationAndSensingData,
    MeshAndBroadcastData,
    OOBSecurityData,
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
from .data_types import (
    CharacteristicInfo,
    DateData,
    ParseFieldError,
    ServiceInfo,
    ValidationAccumulator,
    ValidationResult,
)
from .ead import (
    EAD_ADDRESS_SIZE,
    EAD_IV_SIZE,
    EAD_MIC_SIZE,
    EAD_MIN_SIZE,
    EAD_NONCE_SIZE,
    EAD_RANDOMIZER_SIZE,
    EAD_SESSION_KEY_SIZE,
    EADDecryptResult,
    EADError,
    EADKeyMaterial,
    EncryptedAdvertisingData,
)
from .location import PositionStatus
from .protocols import CharacteristicDataProtocol
from .registry.ad_types import AdTypeInfo
from .registry.appearance_info import AppearanceInfo
from .registry.class_of_device import ClassOfDeviceInfo
from .registry.descriptor_types import DescriptorData, DescriptorInfo
from .registry.uri_schemes import UriSchemeInfo
from .special_values import SpecialValueResult, SpecialValueRule
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
    SpecialValueType,
    TemperatureUnit,
    WeightUnit,
    classify_special_value,
)
from .uri import URIData

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
    "AdTypeInfo",
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
    "CoreAdvertisingData",
    "DirectedAdvertisingData",
    "DateData",
    "DescriptorData",
    "DescriptorInfo",
    "DeviceInfo",
    "DeviceProperties",
    "EAD_ADDRESS_SIZE",
    "EAD_IV_SIZE",
    "EAD_MIC_SIZE",
    "EAD_MIN_SIZE",
    "EAD_NONCE_SIZE",
    "EAD_RANDOMIZER_SIZE",
    "EAD_SESSION_KEY_SIZE",
    "EADDecryptResult",
    "EADError",
    "EADKeyMaterial",
    "ElectricalUnit",
    "EncryptedAdvertisingData",
    "ExtendedAdvertisingData",
    "ExtendedHeaderFlags",
    "GlucoseConcentrationUnit",
    "HeightUnit",
    "LengthUnit",
    "LocationAndSensingData",
    "MeasurementSystem",
    "MeshAndBroadcastData",
    "OOBSecurityData",
    "ParseFieldError",
    "AdvertisementData",
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
    "SpecialValueResult",
    "SpecialValueRule",
    "SpecialValueType",
    "TemperatureUnit",
    "URIData",
    "UriSchemeInfo",
    "ValidationAccumulator",
    "ValidationResult",
    "WeightUnit",
    "classify_special_value",
    "validate_category_id",
]
