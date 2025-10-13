"""Noise (Sound Pressure Level) characteristic implementation.

Per Bluetooth SIG specification (UUID 0x2BE4):
- Data type: uint8 (1 byte)
- Unit: decibel SPL with 1 dB resolution
- Range: 0-253 dB
- Special values: 0xFE (≥254 dB), 0xFF (unknown)
"""

from __future__ import annotations

from typing import cast

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import Uint8Template


class NoiseCharacteristic(BaseCharacteristic):
    """Noise characteristic (0x2BE4) - Sound pressure level measurement.

    Represents sound pressure level in decibels (dB SPL) per SIG specification.
    Uses uint8 format with 1 dB resolution.

    Valid range: 0-253 dB
    Special values:
    - 0xFE (254): Value is 254 dB or greater
    - 0xFF (255): Value is not known
    """

    UNKNOWN_VALUE = 0xFF  # Value is not known
    MAX_OR_GREATER_VALUE = 0xFE  # 254 dB or greater
    MAX_MEASURABLE_VALUE = 254  # Maximum measurable value in dB
    MAX_NORMAL_VALUE = 253  # Maximum normal range value

    _characteristic_name = "Noise"
    _template = Uint8Template()
    _manual_unit: str | None = "dB SPL"

    # Range constraints per SIG spec
    min_value: int | float | None = 0
    max_value: int | float | None = MAX_NORMAL_VALUE

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int | None:
        """Decode noise level with special value handling."""
        raw_value = cast(int, super().decode_value(data, ctx))

        if raw_value == self.MAX_OR_GREATER_VALUE:
            return self.MAX_MEASURABLE_VALUE  # Return minimum of "254 or greater" range
        if raw_value == self.UNKNOWN_VALUE:
            return None  # Represent unknown as None

        return raw_value

    def encode_value(self, data: int | None) -> bytearray:
        """Encode noise level with special value handling."""
        if data is None:
            return super().encode_value(self.UNKNOWN_VALUE)

        if data < 0:
            raise ValueError("Noise level cannot be negative")
        if data >= self.MAX_MEASURABLE_VALUE:
            return super().encode_value(self.MAX_OR_GREATER_VALUE)

        return super().encode_value(data)
