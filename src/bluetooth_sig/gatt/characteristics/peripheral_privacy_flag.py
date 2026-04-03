"""Peripheral Privacy Flag characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class PeripheralPrivacyState(IntEnum):
    """Peripheral privacy state."""

    DISABLED = 0
    ENABLED = 1


class PeripheralPrivacyFlagCharacteristic(BaseCharacteristic[PeripheralPrivacyState]):
    """Peripheral Privacy Flag characteristic (0x2A02).

    org.bluetooth.characteristic.gap.peripheral_privacy_flag

    Indicates whether privacy is enabled (1) or disabled (0).
    """

    expected_length: int = 1
    _template = EnumTemplate.uint8(PeripheralPrivacyState)
