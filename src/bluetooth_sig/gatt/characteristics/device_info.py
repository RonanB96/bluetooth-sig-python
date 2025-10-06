"""Device Information Service characteristics."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class ManufacturerNameStringCharacteristic(BaseCharacteristic):
    """Manufacturer Name String characteristic."""

    _template = Utf8StringTemplate()


class ModelNumberStringCharacteristic(BaseCharacteristic):
    """Model Number String characteristic."""

    _template = Utf8StringTemplate()


class SerialNumberStringCharacteristic(BaseCharacteristic):
    """Serial Number String characteristic."""

    _template = Utf8StringTemplate()


class FirmwareRevisionStringCharacteristic(BaseCharacteristic):
    """Firmware Revision String characteristic."""

    _template = Utf8StringTemplate()


class HardwareRevisionStringCharacteristic(BaseCharacteristic):
    """Hardware Revision String characteristic."""

    _template = Utf8StringTemplate()


class SoftwareRevisionStringCharacteristic(BaseCharacteristic):
    """Software Revision String characteristic."""

    _template = Utf8StringTemplate()
