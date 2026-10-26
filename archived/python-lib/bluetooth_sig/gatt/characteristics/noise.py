"""Noise (Sound Pressure Level) characteristic implementation.

Per Bluetooth SIG specification (UUID 0x2BE4):
- Data type: uint8 (1 byte)
- Unit: decibel SPL with 1 dB resolution
- Range: 0-253 dB
- Special values: 0xFE (≥254 dB), 0xFF (unknown)
"""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import Uint8Template


class NoiseCharacteristic(BaseCharacteristic[int]):
    """Noise characteristic (0x2BE4) - Sound pressure level measurement.

    Represents sound pressure level in decibels (dB SPL) per SIG specification.
    Uses uint8 format with 1 dB resolution.
    """

    _template = Uint8Template()
    _manual_unit: str | None = "dB SPL"
