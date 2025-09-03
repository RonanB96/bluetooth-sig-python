"""GATT package initialization."""

from .characteristics.base import BaseCharacteristic
from .services.base import BaseGattService as BaseService
from .uuid_registry import UuidInfo, UuidRegistry

__all__ = [
    "BaseService",
    "BaseCharacteristic",
    "UuidRegistry",
    "UuidInfo",
]
