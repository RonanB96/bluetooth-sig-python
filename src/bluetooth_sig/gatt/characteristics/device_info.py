"""Device Information Service characteristics - re-exports for backward compatibility."""

from __future__ import annotations

from .firmware_revision_string import FirmwareRevisionStringCharacteristic
from .hardware_revision_string import HardwareRevisionStringCharacteristic
from .software_revision_string import SoftwareRevisionStringCharacteristic

__all__ = [
    "FirmwareRevisionStringCharacteristic",
    "HardwareRevisionStringCharacteristic",
    "SoftwareRevisionStringCharacteristic",
]
