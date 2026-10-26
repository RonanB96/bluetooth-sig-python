"""ESL Current Absolute Time characteristic implementation."""

from __future__ import annotations

from ...types.gatt_enums import CharacteristicRole
from ..constants import UINT32_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class ESLCurrentAbsoluteTimeCharacteristic(BaseCharacteristic[int]):
    """ESL Current Absolute Time characteristic (0x2BF9).

    org.bluetooth.characteristic.esl_current_absolute_time

    A uint32 representing milliseconds since the ESL epoch.
    """

    _manual_role = CharacteristicRole.STATUS
    expected_length: int = 4  # uint32
    min_length: int = 4
    min_value = 0
    max_value = UINT32_MAX

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> int:
        """Parse ESL absolute time (uint32 milliseconds).

        Args:
            data: Raw bytes (4 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Milliseconds since ESL epoch as integer.

        """
        return DataParser.parse_int32(data, 0, signed=False)

    def _encode_value(self, data: int) -> bytearray:
        """Encode ESL absolute time to bytes.

        Args:
            data: Milliseconds since ESL epoch as integer.

        Returns:
            Encoded bytes (4 bytes).

        """
        return DataParser.encode_int32(data, signed=False)
