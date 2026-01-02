"""Software Revision String characteristic implementation."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Utf8StringTemplate


class SoftwareRevisionStringCharacteristic(BaseCharacteristic):
    """Software Revision String characteristic (0x2A28).

    org.bluetooth.characteristic.software_revision_string

    Represents the software revision as a UTF-8 string.
    """

    _template = Utf8StringTemplate()
    min_length = 0
