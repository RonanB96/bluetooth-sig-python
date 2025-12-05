"""Latitude characteristic implementation."""

from __future__ import annotations

from bluetooth_sig.types.context import CharacteristicContext

from .base import BaseCharacteristic
from .utils import DataParser


class LatitudeCharacteristic(BaseCharacteristic):
    """Latitude characteristic (0x2AAE).

    org.bluetooth.characteristic.latitude

    Latitude characteristic.
    """

    # Geographic coordinate constants
    BYTE_LENGTH = 4  # sint32
    DEGREE_SCALING_FACTOR = 1e-7  # 10^-7 degrees per unit
    LATITUDE_MIN = -90.0
    LATITUDE_MAX = 90.0

    expected_length = BYTE_LENGTH
    min_value = LATITUDE_MIN
    max_value = LATITUDE_MAX
    expected_type = float

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Parse latitude from sint32 * 10^-7 degrees."""
        raw = DataParser.parse_int32(data, 0, signed=True)
        return raw * self.DEGREE_SCALING_FACTOR

    def encode_value(self, data: float) -> bytearray:
        """Encode latitude to sint32 * 10^-7 degrees."""
        raw = int(data / self.DEGREE_SCALING_FACTOR)
        return DataParser.encode_int32(raw, signed=True)
