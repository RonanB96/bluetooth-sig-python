"""Supported Unread Alert Category characteristic (0x2A48) implementation.

Represents which alert categories the server supports for unread alerts.
Used by Alert Notification Service (0x1811).

Based on Bluetooth SIG GATT Specification:
- Supported Unread Alert Category: 2 bytes (16-bit Category ID Bit Mask)
"""

from __future__ import annotations

from ...types import AlertCategoryBitMask
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class SupportedUnreadAlertCategoryCharacteristic(BaseCharacteristic[AlertCategoryBitMask]):
    """Supported Unread Alert Category characteristic (0x2A48).

    Represents which alert categories the server supports for unread alerts
    using a 16-bit bitmask.

    Structure (2 bytes):
    - Category ID Bit Mask: uint16 (bit 0=Simple Alert, bit 1=Email, etc.)
      Bits 10-15 reserved for future use

    Used by Alert Notification Service (0x1811).
    """

    # YAML specifies size: 1 or 2 (variable length struct)
    min_length: int | None = 1
    max_length: int | None = 2

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> AlertCategoryBitMask:
        """Decode Supported Unread Alert Category data from bytes.

        Args:
            data: Raw characteristic data (2 bytes)
            ctx: Optional characteristic context

        Returns:
            AlertCategoryBitMask flags

        Raises:
            ValueError: If data is insufficient

        """
        if len(data) < 2:
            raise ValueError(
                f"Insufficient data for Supported Unread Alert Category: expected 2 bytes, got {len(data)}"
            )

        mask_value = DataParser.parse_int16(data, 0, signed=False)
        return AlertCategoryBitMask(mask_value)

    def _encode_value(self, data: AlertCategoryBitMask | int) -> bytearray:
        """Encode Supported Unread Alert Category data to bytes.

        Args:
            data: AlertCategoryBitMask or int value

        Returns:
            Encoded supported unread alert category (2 bytes)

        """
        int_value = int(data) if isinstance(data, AlertCategoryBitMask) else data
        return DataParser.encode_int16(int_value, signed=False)
