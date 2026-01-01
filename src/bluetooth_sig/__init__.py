"""Bluetooth SIG Standards Library for pure SIG standard interpretation.

A framework-agnostic library for parsing and interpreting Bluetooth SIG
standards, including GATT characteristics, services, and UUID resolution.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .advertising import (
    AdvertisingDataInterpreter,
    AdvertisingInterpreterInfo,
    AdvertisingInterpreterRegistry,
    AdvertisingPDUParser,
    DataSource,
    DictKeyProvider,
    EncryptionKeyProvider,
    advertising_interpreter_registry,
)
from .core.async_context import AsyncParsingSession
from .core.translator import BluetoothSIGTranslator
from .gatt.characteristics.base import BaseCharacteristic, CharacteristicData
from .gatt.characteristics.registry import CharacteristicRegistry
from .gatt.services.base import BaseGattService
from .gatt.services.registry import GattServiceRegistry
from .types.base_types import SIGInfo
from .types.data_types import CharacteristicInfo, ServiceInfo, ValidationResult

try:
    from ._version import __version__
except ImportError:
    _version_result = subprocess.run(
        ["git", "describe", "--tags"],
        capture_output=True,
        text=True,
        check=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    __version__ = _version_result.stdout.strip().lstrip("v")

__all__ = [
    # Advertising PDU parsing
    "AdvertisingPDUParser",
    # Advertising data interpretation (vendor-specific)
    "AdvertisingDataInterpreter",
    "AdvertisingInterpreterInfo",
    "AdvertisingInterpreterRegistry",
    "advertising_interpreter_registry",
    "DataSource",
    "DictKeyProvider",
    "EncryptionKeyProvider",
    # Core
    "AsyncParsingSession",
    "BaseCharacteristic",
    "BaseGattService",
    "BluetoothSIGTranslator",
    "CharacteristicData",
    "CharacteristicInfo",
    "CharacteristicRegistry",
    "GattServiceRegistry",
    "ServiceInfo",
    "SIGInfo",
    "ValidationResult",
    "__version__",
]
