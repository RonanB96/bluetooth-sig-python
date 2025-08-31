"""GATT package initialization."""

from .characteristics.base import BaseCharacteristic
from .services.base import BaseGattService
from .uuid_registry import UuidInfo, UuidRegistry

__all__ = [
    "BaseGattService",
    "BaseCharacteristic",
    "UuidRegistry",
    "UuidInfo",
]
