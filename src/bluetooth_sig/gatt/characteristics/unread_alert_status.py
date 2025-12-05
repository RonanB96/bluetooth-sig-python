"""Unread Alert Status characteristic (0x2A45) implementation.

Represents the number of unread alerts in a specific category.
Used by Alert Notification Service (0x1811).

Based on Bluetooth SIG GATT Specification:
- Unread Alert Status: 2 bytes (Category ID + Unread Count)
"""

from __future__ import annotations

import msgspec

from ...types import AlertCategoryID, validate_category_id
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class UnreadAlertStatusData(msgspec.Struct):
    """Unread Alert Status characteristic data structure."""

    category_id: AlertCategoryID
    unread_count: int  # 0-254, 255 means >254


class UnreadAlertStatusCharacteristic(BaseCharacteristic):
    """Unread Alert Status characteristic (0x2A45).

    Represents the number of unread alerts in a specific category.

    Structure (2 bytes):
    - Category ID: uint8 (0=Simple Alert, 1=Email, etc.)
    - Unread Count: uint8 (0-254, 255 means more than 254 unread alerts)

    Used by Alert Notification Service (0x1811).
    """

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> UnreadAlertStatusData:
        """Decode Unread Alert Status data from bytes.

        Args:
            data: Raw characteristic data (2 bytes)
            ctx: Optional characteristic context

        Returns:
            UnreadAlertStatusData with all fields

        Raises:
            ValueError: If data is insufficient or contains invalid values

        """
        if len(data) < 2:
            raise ValueError(f"Insufficient data for Unread Alert Status: expected 2 bytes, got {len(data)}")

        # Parse Category ID (1 byte)
        category_id_raw = DataParser.parse_int8(data, 0, signed=False)
        category_id = validate_category_id(category_id_raw)

        # Parse Unread Count (1 byte)
        unread_count = DataParser.parse_int8(data, 1, signed=False)

        return UnreadAlertStatusData(
            category_id=category_id,
            unread_count=unread_count,
        )

    def encode_value(self, data: UnreadAlertStatusData) -> bytearray:
        """Encode Unread Alert Status data to bytes.

        Args:
            data: UnreadAlertStatusData to encode

        Returns:
            Encoded unread alert status (2 bytes)

        Raises:
            ValueError: If data contains invalid values

        """
        result = bytearray()

        # Encode Category ID (1 byte)
        category_id_value = int(data.category_id)
        validate_category_id(category_id_value)  # Validate the category ID value
        result.append(category_id_value)

        # Encode Unread Count (1 byte)
        result.append(data.unread_count)

        return result
