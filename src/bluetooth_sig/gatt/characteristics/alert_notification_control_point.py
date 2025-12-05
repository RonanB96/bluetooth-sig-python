"""Alert Notification Control Point characteristic (0x2A44) implementation.

Control point for enabling/disabling alert notifications and triggering immediate notifications.
Used by Alert Notification Service (0x1811).

Based on Bluetooth SIG GATT Specification:
- Alert Notification Control Point: 2 bytes (Command ID + Category ID)
"""

from __future__ import annotations

import msgspec

from ...types import ALERT_COMMAND_MAX, AlertCategoryID, AlertNotificationCommandID, validate_category_id
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AlertNotificationControlPointData(msgspec.Struct):
    """Alert Notification Control Point characteristic data structure."""

    command_id: AlertNotificationCommandID
    category_id: AlertCategoryID


class AlertNotificationControlPointCharacteristic(BaseCharacteristic):
    """Alert Notification Control Point characteristic (0x2A44).

    Control point for enabling/disabling notifications and requesting immediate alerts.

    Structure (2 bytes):
    - Command ID: uint8 (0=Enable New Alert, 1=Enable Unread Status, etc.)
    - Category ID: uint8 (0=Simple Alert, 1=Email, etc. - target category for command)

    Commands:
    - 0: Enable New Incoming Alert Notification
    - 1: Enable Unread Category Status Notification
    - 2: Disable New Incoming Alert Notification
    - 3: Disable Unread Category Status Notification
    - 4: Notify New Incoming Alert immediately
    - 5: Notify Unread Category Status immediately

    Used by Alert Notification Service (0x1811).
    """

    def decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None
    ) -> AlertNotificationControlPointData:
        """Decode Alert Notification Control Point data from bytes.

        Args:
            data: Raw characteristic data (2 bytes)
            ctx: Optional characteristic context

        Returns:
            AlertNotificationControlPointData with all fields

        Raises:
            ValueError: If data is insufficient or contains invalid values

        """
        if len(data) < 2:
            raise ValueError(
                f"Insufficient data for Alert Notification Control Point: expected 2 bytes, got {len(data)}"
            )

        # Parse Command ID (1 byte)
        command_id_raw = DataParser.parse_int8(data, 0, signed=False)
        if command_id_raw > ALERT_COMMAND_MAX:
            raise ValueError(f"Invalid command ID: {command_id_raw} (valid range: 0-{ALERT_COMMAND_MAX})")
        command_id = AlertNotificationCommandID(command_id_raw)

        # Parse Category ID (1 byte)
        category_id_raw = DataParser.parse_int8(data, 1, signed=False)
        category_id = validate_category_id(category_id_raw)

        return AlertNotificationControlPointData(
            command_id=command_id,
            category_id=category_id,
        )

    def encode_value(self, data: AlertNotificationControlPointData) -> bytearray:
        """Encode Alert Notification Control Point data to bytes.

        Args:
            data: AlertNotificationControlPointData to encode

        Returns:
            Encoded alert notification control point (2 bytes)

        Raises:
            ValueError: If data contains invalid values

        """
        result = bytearray()

        # Encode Command ID (1 byte)
        command_id_value = int(data.command_id)
        if command_id_value > ALERT_COMMAND_MAX:
            raise ValueError(f"Invalid command ID: {command_id_value} (valid range: 0-{ALERT_COMMAND_MAX})")
        result.append(command_id_value)

        # Encode Category ID (1 byte)
        category_id_value = int(data.category_id)
        validate_category_id(category_id_value)  # Validate the category ID value
        result.append(category_id_value)

        return result
