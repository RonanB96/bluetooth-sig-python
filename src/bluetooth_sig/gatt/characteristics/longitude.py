"""Longitude characteristic implementation."""

from __future__ import annotations

from bluetooth_sig.types.context import CharacteristicContext

from .base import BaseCharacteristic
from .utils import DataParser


class LongitudeCharacteristic(BaseCharacteristic):
    """Longitude characteristic (0x2AAF).

    org.bluetooth.characteristic.longitude

    Longitude characteristic.
    """

    # Geographic coordinate constants
    BYTE_LENGTH = 4  # sint32
    DEGREE_SCALING_FACTOR = 1e-7  # 10^-7 degrees per unit
    LONGITUDE_MIN = -180.0
    LONGITUDE_MAX = 180.0

    expected_length = BYTE_LENGTH
    min_value = LONGITUDE_MIN
    max_value = LONGITUDE_MAX
    expected_type = float

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Parse longitude from sint32 * 10^-7 degrees."""
        raw = DataParser.parse_int32(data, 0, signed=True)
        return raw * self.DEGREE_SCALING_FACTOR

    def encode_value(self, data: float) -> bytearray:
        """Encode longitude to sint32 * 10^-7 degrees."""
        if not self.LONGITUDE_MIN <= data <= self.LONGITUDE_MAX:
            raise ValueError(f"Longitude {data} out of range [{self.LONGITUDE_MIN}, {self.LONGITUDE_MAX}]")
        raw = int(data / self.DEGREE_SCALING_FACTOR)
        return DataParser.encode_int32(raw, signed=True)
