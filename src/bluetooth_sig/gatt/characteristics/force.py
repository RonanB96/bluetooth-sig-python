"""Force characteristic implementation."""

from __future__ import annotations

from ..constants import SINT32_MAX, SINT32_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class ForceValues:  # pylint: disable=too-few-public-methods
    """Special values for Force characteristic per Bluetooth SIG specification."""

    VALUE_NOT_KNOWN = 0x7FFFFFFF


class ForceCharacteristic(BaseCharacteristic):
    """Force characteristic (0x2C07).

    org.bluetooth.characteristic.force

    The Force characteristic is used to represent the force being applied to an object along a given axis.
    """

    expected_length: int = 4  # sint32

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
        """Decode force characteristic.

        Decodes a 32-bit signed integer representing force in 0.001 N increments
        per Bluetooth SIG Force characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Force in Newtons, or None if value is not known

        Raises:
            InsufficientDataError: If data is not exactly 4 bytes
        """
        raw_value = DataParser.parse_int32(data, 0, signed=True)
        if raw_value == ForceValues.VALUE_NOT_KNOWN:
            return None
        return raw_value * 0.001

    def encode_value(self, data: float) -> bytearray:
        """Encode force value."""
        if not SINT32_MIN <= data <= SINT32_MAX - 1:
            raise ValueError(f"Force value {data} out of valid range")
        raw_value = int(data / 0.001)
        return DataParser.encode_int32(raw_value, signed=True)
