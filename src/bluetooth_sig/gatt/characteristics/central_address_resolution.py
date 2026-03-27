"""Central Address Resolution characteristic."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class CentralAddressResolutionSupport(IntEnum):
    """Central Address Resolution support status."""

    NOT_SUPPORTED = 0
    SUPPORTED = 1


class CentralAddressResolutionCharacteristic(BaseCharacteristic[CentralAddressResolutionSupport]):
    """Central Address Resolution characteristic (0x2AA6).

    org.bluetooth.characteristic.central_address_resolution

    Indicates whether the Central Address Resolution is supported (1) or not (0).
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(CentralAddressResolutionSupport)
