"""Data types for Bluetooth SIG standards.

Advertising types are now in the bluetooth_sig.types.advertising subpackage:
    - pdu: PDUType, BLEAdvertisingPDU, PDUHeaderFlags, etc.
    - extended: CTEInfo, AdvertisingDataInfo, AuxiliaryPointer, SyncInfo
    - flags: BLEAdvertisingFlags
    - features: LEFeatures, LEFeatureBits
    - ad_structures: All *Data struct types (CoreAdvertisingData, etc.)
    - result: AdvertisingData, AdvertisementData
"""

from __future__ import annotations

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
)
from .appearance import AppearanceData
from .base_types import SIGInfo
from .battery import BatteryChargeLevel, BatteryChargeState, BatteryChargingType, BatteryFaultReason
from .company import CompanyIdentifier, ManufacturerData
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
from .gatt_enums import CharacteristicRole
from .location import PositionStatus
from .mesh import (
    DEVICE_UUID_LENGTH,
    NETWORK_ID_LENGTH,
    NETWORK_KEY_LENGTH,
    MeshBeaconType,
    MeshCapabilities,
    MeshMessage,
    ProvisioningBearerData,
    ProvisioningPDUType,
    SecureNetworkBeacon,
    UnprovisionedDeviceBeacon,
)
from .protocols import CharacteristicProtocol
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
    "ALERT_CATEGORY_RESERVED_MAX",
    "ALERT_CATEGORY_RESERVED_MIN",
    "ALERT_CATEGORY_SERVICE_SPECIFIC_MIN",
    "ALERT_COMMAND_MAX",
    "ALERT_TEXT_MAX_LENGTH",
    "EAD_ADDRESS_SIZE",
    "EAD_IV_SIZE",
    "EAD_MIC_SIZE",
    "EAD_MIN_SIZE",
    "EAD_NONCE_SIZE",
    "EAD_RANDOMIZER_SIZE",
    "EAD_SESSION_KEY_SIZE",
    "UNREAD_COUNT_MAX",
    "UNREAD_COUNT_MORE_THAN_MAX",
    "AdTypeInfo",
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
    "CharacteristicContext",
    "CharacteristicInfo",
    "CharacteristicProtocol",
    "CharacteristicRole",
    "ClassOfDeviceInfo",
    "CompanyIdentifier",
    "ConcentrationUnit",
    "DateData",
    "DescriptorData",
    "DescriptorInfo",
    "DeviceInfo",
    "EADDecryptResult",
    "EADError",
    "EADKeyMaterial",
    "ElectricalUnit",
    "EncryptedAdvertisingData",
    "GlucoseConcentrationUnit",
    "HeightUnit",
    "LengthUnit",
    "ManufacturerData",
    "MeasurementSystem",
    "MeshBeaconType",
    "MeshCapabilities",
    "MeshMessage",
    "NETWORK_ID_LENGTH",
    "NETWORK_KEY_LENGTH",
    "DEVICE_UUID_LENGTH",
    "ParseFieldError",
    "ProvisioningBearerData",
    "PercentageUnit",
    "PhysicalUnit",
    "PositionStatus",
    "PressureUnit",
    "ProvisioningPDUType",
    "SIGInfo",
    "SecureNetworkBeacon",
    "ServiceInfo",
    "SoundUnit",
    "SpecialValueResult",
    "SpecialValueRule",
    "SpecialValueType",
    "TemperatureUnit",
    "URIData",
    "UnprovisionedDeviceBeacon",
    "UriSchemeInfo",
    "ValidationAccumulator",
    "ValidationResult",
    "WeightUnit",
    "classify_special_value",
]
