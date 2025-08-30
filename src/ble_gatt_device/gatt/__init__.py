"""GATT package initialization."""

from .services.base import BaseGattService
from .characteristics.base import BaseCharacteristic
from .uuid_registry import UuidRegistry, UuidInfo

__all__ = [
    "BaseGattService",
    "BaseCharacteristic",
    "UuidRegistry",
    "UuidInfo",
]
