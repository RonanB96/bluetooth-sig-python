"""Device Information Service characteristics."""

from __future__ import annotations

from dataclasses import dataclass

from .templates import StringCharacteristic


@dataclass
class ManufacturerNameStringCharacteristic(StringCharacteristic):
    """Manufacturer Name String characteristic."""

    _characteristic_name: str = "Manufacturer Name String"


@dataclass
class ModelNumberStringCharacteristic(StringCharacteristic):
    """Model Number String characteristic."""

    _characteristic_name: str = "Model Number String"


@dataclass
class SerialNumberStringCharacteristic(StringCharacteristic):
    """Serial Number String characteristic."""

    _characteristic_name: str = "Serial Number String"


@dataclass
class FirmwareRevisionStringCharacteristic(StringCharacteristic):
    """Firmware Revision String characteristic."""

    _characteristic_name: str = "Firmware Revision String"


@dataclass
class HardwareRevisionStringCharacteristic(StringCharacteristic):
    """Hardware Revision String characteristic."""

    _characteristic_name: str = "Hardware Revision String"


@dataclass
class SoftwareRevisionStringCharacteristic(StringCharacteristic):
    """Software Revision String characteristic."""

    _characteristic_name: str = "Software Revision String"
