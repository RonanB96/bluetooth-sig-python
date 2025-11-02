"""Device Information Service characteristics."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class ManufacturerNameStringCharacteristic(BaseCharacteristic):
    """Manufacturer Name String characteristic (0x2A29).

    org.bluetooth.characteristic.manufacturer_name_string

    Manufacturer Name String characteristic.
    """

    _template = Utf8StringTemplate()


class ModelNumberStringCharacteristic(BaseCharacteristic):
    """Model Number String characteristic (0x2A24).

    org.bluetooth.characteristic.model_number_string

    Model Number String characteristic.
    """

    _template = Utf8StringTemplate()


class SerialNumberStringCharacteristic(BaseCharacteristic):
    """Serial Number String characteristic (0x2A25).

    org.bluetooth.characteristic.serial_number_string

    Serial Number String characteristic.
    """

    _template = Utf8StringTemplate()


class FirmwareRevisionStringCharacteristic(BaseCharacteristic):
    """Firmware Revision String characteristic (0x2A26).

    org.bluetooth.characteristic.firmware_revision_string

    Firmware Revision String characteristic.
    """

    _template = Utf8StringTemplate()


class HardwareRevisionStringCharacteristic(BaseCharacteristic):
    """Hardware Revision String characteristic (0x2A27).

    org.bluetooth.characteristic.hardware_revision_string

    Hardware Revision String characteristic.
    """

    _template = Utf8StringTemplate()


class SoftwareRevisionStringCharacteristic(BaseCharacteristic):
    """Software Revision String characteristic (0x2A28).

    org.bluetooth.characteristic.software_revision_string

    Software Revision String characteristic.
    """

    _template = Utf8StringTemplate()
