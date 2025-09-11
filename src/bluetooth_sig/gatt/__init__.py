"""GATT package initialization."""

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
from .services.base import BaseGattService as BaseService
from .uuid_registry import UuidInfo, UuidRegistry

__all__ = [
    "BaseService",
    "BaseCharacteristic",
    "UuidRegistry",
    "UuidInfo",
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
