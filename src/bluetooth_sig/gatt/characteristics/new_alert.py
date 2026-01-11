"""New Alert characteristic (0x2A46) implementation.

Represents a new alert with category, count, and optional text information.
Used by Alert Notification Service (0x1811).

Based on Bluetooth SIG GATT Specification:
- New Alert: Variable length (Category ID + Number of New Alert + Text String)
"""

from __future__ import annotations

import msgspec

from ...types import ALERT_TEXT_MAX_LENGTH, AlertCategoryID
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class NewAlertData(msgspec.Struct):
    """New Alert characteristic data structure."""

    category_id: AlertCategoryID
    number_of_new_alert: int  # 0-255
    text_string_information: str  # 0-18 characters


class NewAlertCharacteristic(BaseCharacteristic[NewAlertData]):
    """New Alert characteristic (0x2A46).

    Represents the category, count, and brief text for a new alert.

    Structure (variable length):
    - Category ID: uint8 (0=Simple Alert, 1=Email, etc.)
    - Number of New Alert: uint8 (0-255, count of new alerts)
    - Text String Information: utf8s (0-18 characters, optional brief text)

    Used by Alert Notification Service (0x1811).
    """

    min_length: int = 2  # Category ID(1) + Number of New Alert(1)
    allow_variable_length: bool = True  # Optional text string

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> NewAlertData:
        """Decode New Alert data from bytes.

        Args:
            data: Raw characteristic data (minimum 2 bytes)
            ctx: Optional characteristic context

        Returns:
            NewAlertData with all fields

        Raises:
            ValueError: If data contains invalid values

        """
        # Parse Category ID (1 byte)
        category_id_raw = DataParser.parse_int8(data, 0, signed=False)
        category_id = AlertCategoryID(category_id_raw)

        # Parse Number of New Alert (1 byte)
        number_of_new_alert = DataParser.parse_int8(data, 1, signed=False)

        # Parse Text String Information (remaining bytes, max ALERT_TEXT_MAX_LENGTH characters)
        text_string_information = ""
        if len(data) > 2:
            text_bytes = data[2:]
            if len(text_bytes) > ALERT_TEXT_MAX_LENGTH:
                raise ValueError(f"Text string too long: {len(text_bytes)} bytes (max {ALERT_TEXT_MAX_LENGTH})")
            text_string_information = text_bytes.decode("utf-8", errors="replace")

        return NewAlertData(
            category_id=category_id,
            number_of_new_alert=number_of_new_alert,
            text_string_information=text_string_information,
        )

    def _encode_value(self, data: NewAlertData) -> bytearray:
        """Encode New Alert data to bytes.

        Args:
            data: NewAlertData to encode

        Returns:
            Encoded new alert (variable length)

        Raises:
            ValueError: If data contains invalid values

        """
        result = bytearray()

        # Encode Category ID (1 byte)
        category_id_value = int(data.category_id)
        result.append(category_id_value)

        # Encode Number of New Alert (1 byte)
        result.append(data.number_of_new_alert)

        # Encode Text String Information (utf-8)
        if data.text_string_information:
            text_bytes = data.text_string_information.encode("utf-8")
            if len(text_bytes) > ALERT_TEXT_MAX_LENGTH:
                raise ValueError(f"Text string too long: {len(text_bytes)} bytes (max {ALERT_TEXT_MAX_LENGTH})")
            result.extend(text_bytes)

        return result
