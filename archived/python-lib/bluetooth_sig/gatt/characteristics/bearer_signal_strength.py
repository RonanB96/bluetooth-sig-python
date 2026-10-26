"""Bearer Signal Strength characteristic (0x2BB7)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class BearerSignalStrengthCharacteristic(BaseCharacteristic[int]):
    """Bearer Signal Strength characteristic (0x2BB7).

    org.bluetooth.characteristic.bearer_signal_strength

    Signal strength of the bearer, as an unsigned 8-bit integer.
    """

    _template = Uint8Template()
