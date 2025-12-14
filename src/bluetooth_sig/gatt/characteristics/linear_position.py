"""Linear Position characteristic implementation."""

from __future__ import annotations

from ..constants import SINT32_MAX, SINT32_MIN
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils.data_parser import DataParser


class LinearPositionValues:  # pylint: disable=too-few-public-methods
    """Special values for Linear Position characteristic per Bluetooth SIG specification."""

    VALUE_NOT_KNOWN = 0x7FFFFFFF


class LinearPositionCharacteristic(BaseCharacteristic):
    """Linear Position characteristic (0x2C08).

    org.bluetooth.characteristic.linear_position

    The Linear Position characteristic is used to represent the linear position of an object
    along a given axis and referencing to the device-specific zero point.
    """

    expected_length: int = 4  # sint32

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float | None:
        """Decode linear position characteristic.

        Decodes a 32-bit signed integer representing position in 10^-7 m increments
        per Bluetooth SIG Linear Position characteristic specification.

        Args:
            data: Raw bytes from BLE characteristic (exactly 4 bytes, little-endian)
            ctx: Optional context for parsing (device info, flags, etc.)

        Returns:
            Position in meters, or None if value is not known

        Raises:
            InsufficientDataError: If data is not exactly 4 bytes
        """
        raw_value = DataParser.parse_int32(data, 0, signed=True)
        if raw_value == LinearPositionValues.VALUE_NOT_KNOWN:
            return None
        return raw_value * 1e-7

    def encode_value(self, data: float) -> bytearray:
        """Encode linear position value."""
        if not SINT32_MIN <= data <= SINT32_MAX - 1:
            raise ValueError(f"Linear position value {data} out of valid range")
        raw_value = int(data / 1e-7)
        return DataParser.encode_int32(raw_value, signed=True)
