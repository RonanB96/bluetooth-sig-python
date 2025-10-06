"""Bluetooth SIG Standards Library for pure SIG standard interpretation.
from __future__ import annotations


A framework-agnostic library for parsing and interpreting Bluetooth SIG
standards, including GATT characteristics, services, and UUID
resolution.
"""

from .core import BluetoothSIGTranslator
from .gatt import BaseCharacteristic, BaseService
from .gatt.characteristics import CharacteristicRegistry
from .gatt.services import GattServiceRegistry
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
    "BaseService",
    "CharacteristicData",
    "CharacteristicInfo",
    "CharacteristicRegistry",
    "GattServiceRegistry",
    "ServiceInfo",
    "SIGInfo",
    "ValidationResult",
]
