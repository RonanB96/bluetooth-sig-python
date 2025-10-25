"""Bluetooth SIG Standards Library for pure SIG standard interpretation.

A framework-agnostic library for parsing and interpreting Bluetooth SIG
standards, including GATT characteristics, services, and UUID
resolution.
"""

from __future__ import annotations

from .core import BluetoothSIGTranslator
from .gatt import BaseCharacteristic, BaseGattService
from .gatt.characteristics import CharacteristicRegistry
from .gatt.services import GattServiceRegistry
from .registry import members_registry
from .types import (
    CharacteristicData,
    CharacteristicInfo,
    ServiceInfo,
    SIGInfo,
    ValidationResult,
)

__version__ = "0.3.0"

__all__ = [
    "BluetoothSIGTranslator",
    "BaseCharacteristic",
    "BaseGattService",
    "CharacteristicData",
    "CharacteristicInfo",
    "CharacteristicRegistry",
    "GattServiceRegistry",
    "ServiceInfo",
    "SIGInfo",
    "ValidationResult",
    "members_registry",
]
