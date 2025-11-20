"""Latitude characteristic implementation."""

from __future__ import annotations

from bluetooth_sig.types.context import CharacteristicContext

from .base import BaseCharacteristic


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
        if len(data) != self.BYTE_LENGTH:
            raise ValueError(f"Expected {self.BYTE_LENGTH} bytes, got {len(data)}")
        raw = int.from_bytes(data, byteorder="little", signed=True)
        return raw * self.DEGREE_SCALING_FACTOR

    def encode_value(self, data: float) -> bytearray:
        """Encode latitude to sint32 * 10^-7 degrees."""
        if not self.LATITUDE_MIN <= data <= self.LATITUDE_MAX:
            raise ValueError(f"Latitude {data} out of range [{self.LATITUDE_MIN}, {self.LATITUDE_MAX}]")
        raw = int(data / self.DEGREE_SCALING_FACTOR)
        return bytearray(raw.to_bytes(self.BYTE_LENGTH, byteorder="little", signed=True))
