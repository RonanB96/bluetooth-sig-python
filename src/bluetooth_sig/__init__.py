"""Bluetooth SIG Standards Library for pure SIG standard interpretation.

A framework-agnostic library for parsing and interpreting Bluetooth SIG
standards, including GATT characteristics, services, and UUID resolution.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# Primary API
from .core.async_context import AsyncParsingSession
from .core.translator import BluetoothSIGTranslator
from .device.device import Device

# Essential types for type hints
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
    # Primary API
    "AsyncParsingSession",
    "BluetoothSIGTranslator",
    # Essential types for type hints
    "CharacteristicInfo",
    "Device",
    "SIGInfo",
    "ServiceInfo",
    "ValidationResult",
    # Version
    "__version__",
]
