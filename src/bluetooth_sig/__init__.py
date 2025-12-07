"""Bluetooth SIG Standards Library for pure SIG standard interpretation.

A framework-agnostic library for parsing and interpreting Bluetooth SIG
standards, including GATT characteristics, services, and UUID
resolution.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .core import AsyncParsingSession, BluetoothSIGTranslator
from .gatt import BaseCharacteristic, BaseGattService
from .gatt.characteristics import CharacteristicRegistry
from .gatt.characteristics.base import CharacteristicData
from .gatt.services import GattServiceRegistry
from .registry.uuids.members import members_registry
from .types import CharacteristicInfo, ServiceInfo, SIGInfo, ValidationResult

# Get version from hatchling-generated file, fallback to git describe
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
    "AsyncParsingSession",
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
