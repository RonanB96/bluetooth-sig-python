"""Object Name characteristic implementation."""

from __future__ import annotations

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

_MAX_NAME_LENGTH = 120  # Maximum UTF-8 string length per OTS spec


class ObjectNameCharacteristic(BaseCharacteristic[str]):
    """Object Name characteristic (0x2ABE).

    org.bluetooth.characteristic.object_name

    A UTF-8 string (0-120 bytes) representing the name of an object
    in the Object Transfer Service (OTS).
    """

    min_length: int = 0
    max_length: int = _MAX_NAME_LENGTH

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> str:
        """Parse object name (UTF-8 string).

        Args:
            data: Raw bytes (0-120 bytes).
            ctx: Optional CharacteristicContext.
            validate: Whether to validate ranges (default True).

        Returns:
            Object name as string.

        """
        return DataParser.parse_utf8_string(data)

    def _encode_value(self, data: str) -> bytearray:
        """Encode object name to bytes.

        Args:
            data: Object name as string (0-120 bytes when encoded).

        Returns:
            Encoded bytes.

        """
        return bytearray(data.encode("utf-8"))
