"""Alert Notification Control Point characteristic (0x2A44) implementation.

Control point for enabling/disabling alert notifications and triggering immediate notifications.
Used by Alert Notification Service (0x1811).

Based on Bluetooth SIG GATT Specification:
- Alert Notification Control Point: 2 bytes (Command ID + Category ID)
"""

from __future__ import annotations

import msgspec

from ...types import AlertCategoryID, AlertNotificationCommandID
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AlertNotificationControlPointData(msgspec.Struct):
    """Alert Notification Control Point characteristic data structure."""

    command_id: AlertNotificationCommandID
    category_id: AlertCategoryID


class AlertNotificationControlPointCharacteristic(BaseCharacteristic[AlertNotificationControlPointData]):
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

    min_length: int = 2  # Command ID + Category ID
    allow_variable_length: bool = True  # Some commands may have additional data

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None
    ) -> AlertNotificationControlPointData:
        """Decode Alert Notification Control Point data from bytes.

        Args:
            data: Raw characteristic data (2 bytes, length validated by BaseCharacteristic)
            ctx: Optional characteristic context

        Returns:
            AlertNotificationControlPointData with all fields

        Raises:
            ValueError: If data contains invalid values

        """
        # Parse Command ID (1 byte)
        command_id = AlertNotificationCommandID(DataParser.parse_int8(data, 0, signed=False))

        # Parse Category ID (1 byte)
        category_id_raw = DataParser.parse_int8(data, 1, signed=False)
        category_id = AlertCategoryID(category_id_raw)

        return AlertNotificationControlPointData(
            command_id=command_id,
            category_id=category_id,
        )

    def _encode_value(self, data: AlertNotificationControlPointData) -> bytearray:
        """Encode Alert Notification Control Point data to bytes.

        Args:
            data: AlertNotificationControlPointData to encode

        Returns:
            Encoded alert notification control point (2 bytes)

        Raises:
            ValueError: If data contains invalid values

        """
        result = bytearray()
        result.append(int(data.command_id))
        result.append(int(data.category_id))
        return result
