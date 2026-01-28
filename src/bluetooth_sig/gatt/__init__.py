"""GATT package - characteristics, services, and UUID resolution."""

from __future__ import annotations

from ..types.registry import CharacteristicSpec, FieldInfo, UnitMetadata
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
from .uuid_registry import UuidRegistry, uuid_registry

__all__ = [
    # Constants
    "ABSOLUTE_ZERO_CELSIUS",
    "PERCENTAGE_MAX",
    "SINT8_MAX",
    "SINT8_MIN",
    "SINT16_MAX",
    "TEMPERATURE_RESOLUTION",
    "UINT8_MAX",
    "UINT16_MAX",
    "BaseCharacteristic",
    "BaseGattService",
    # Exceptions
    "BluetoothSIGError",
    "CharacteristicError",
    "CharacteristicSpec",
    "DataParsingError",
    "FieldInfo",
    "ServiceError",
    "UUIDResolutionError",
    "UnitMetadata",
    "UuidRegistry",
    "ValueRangeError",
    "uuid_registry",
]
