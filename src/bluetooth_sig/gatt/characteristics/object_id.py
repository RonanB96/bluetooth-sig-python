"""Object ID characteristic implementation."""

from __future__ import annotations

from ..constants import UINT48_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ObjectIdCharacteristic(BaseCharacteristic[int]):
    """Object ID characteristic (0x2AC3).

    org.bluetooth.characteristic.object_id

    A 48-bit locally unique object identifier used by the Object
    Transfer Service (OTS).
    """

    expected_length: int = 6  # uint48
    min_length: int = 6
    min_value = 0
    max_value = UINT48_MAX

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        """Parse object ID (uint48).

        Args:
            data: Raw bytes (6 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Object ID as integer.

        """
        return DataParser.parse_int48(data, 0, signed=False)

    def _encode_value(self, data: int) -> bytearray:
        """Encode object ID to bytes.

        Args:
            data: Object ID as integer (0 to 2^48-1).

        Returns:
            Encoded bytes (6 bytes).

        """
        return DataParser.encode_int48(data, signed=False)
