"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from .advertising import (
    BLEAdvertisementTypes,
    BLEAdvertisingFlags,
    BLEAdvertisingPDU,
    BLEExtendedHeader,
    DeviceAdvertiserData,
    ExtendedHeaderMode,
    ParsedADStructures,
    PDUConstants,
    PDUFlags,
    PDUType,
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
from .base_types import SIGInfo
from .battery import BatteryChargeLevel, BatteryChargeState, BatteryChargingType, BatteryFaultReason
from .context import CharacteristicContext, DeviceInfo
from .data_types import (
    CharacteristicData,
    CharacteristicInfo,
    CharacteristicRegistration,
    ParseFieldError,
    ServiceInfo,
    ServiceRegistration,
    ValidationResult,
)
from .descriptor_types import DescriptorData, DescriptorInfo
from .protocols import CharacteristicDataProtocol
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
    "AlertCategoryBitMask",
    "AlertCategoryID",
    "AlertNotificationCommandID",
    "validate_category_id",
    "AngleUnit",
    "BatteryChargeLevel",
    "BatteryChargeState",
    "BatteryChargingType",
    "BatteryFaultReason",
    "BLEAdvertisementTypes",
    "BLEAdvertisingFlags",
    "BLEAdvertisingPDU",
    "BLEExtendedHeader",
    "CharacteristicContext",
    "CharacteristicData",
    "CharacteristicDataProtocol",
    "CharacteristicInfo",
    "CharacteristicRegistration",
    "ConcentrationUnit",
    "DescriptorData",
    "DescriptorInfo",
    "DeviceAdvertiserData",
    "DeviceInfo",
    "ElectricalUnit",
    "ExtendedHeaderMode",
    "GlucoseConcentrationUnit",
    "HeightUnit",
    "LengthUnit",
    "MeasurementSystem",
    "ParsedADStructures",
    "ParseFieldError",
    "PDUConstants",
    "PDUFlags",
    "PDUType",
    "PercentageUnit",
    "PhysicalUnit",
    "PressureUnit",
    "ServiceInfo",
    "ServiceRegistration",
    "SIGInfo",
    "SoundUnit",
    "TemperatureUnit",
    "ValidationResult",
    "WeightUnit",
]
