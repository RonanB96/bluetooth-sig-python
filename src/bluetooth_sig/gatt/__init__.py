"""GATT package - characteristics, services, and UUID resolution."""

from __future__ import annotations

from .characteristics.base import BaseCharacteristic
from .constants import (
    ABSOLUTE_ZERO_CELSIUS,
    PERCENTAGE_MAX,
    SINT8_MAX,
    SINT8_MIN,
    SINT16_MAX,
    TEMPERATURE_RESOLUTION,
    UINT8_MAX,
    UINT16_MAX,
)
from .exceptions import (
    BluetoothSIGError,
    CharacteristicError,
    DataParsingError,
    ServiceError,
    UUIDResolutionError,
    ValueRangeError,
)
from .services.base import BaseGattService
from .uuid_registry import CharacteristicSpec, FieldInfo, UnitMetadata, UuidRegistry, uuid_registry

__all__ = [
    "BaseGattService",
    "BaseCharacteristic",
    "CharacteristicSpec",
    "FieldInfo",
    "UnitMetadata",
    "UuidRegistry",
    "uuid_registry",
    # Constants
    "ABSOLUTE_ZERO_CELSIUS",
    "PERCENTAGE_MAX",
    "SINT16_MAX",
    "SINT8_MAX",
    "SINT8_MIN",
    "TEMPERATURE_RESOLUTION",
    "UINT16_MAX",
    "UINT8_MAX",
    # Exceptions
    "BluetoothSIGError",
    "CharacteristicError",
    "DataParsingError",
    "ServiceError",
    "UUIDResolutionError",
    "ValueRangeError",
]
