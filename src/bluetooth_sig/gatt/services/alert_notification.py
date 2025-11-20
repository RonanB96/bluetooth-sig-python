"""Alert Notification Service implementation."""

from __future__ import annotations

from typing import ClassVar

from ..characteristics.registry import CharacteristicName
from .base import BaseGattService


class AlertNotificationService(BaseGattService):
    """Alert Notification Service implementation.

    Exposes alert information from a device to a peer device.

    Contains characteristics related to alert notifications:
    - Supported New Alert Category - Required
    - New Alert - Optional
    - Supported Unread Alert Category - Required
    - Unread Alert Status - Optional
    - Alert Notification Control Point - Required
    """

    service_characteristics: ClassVar[dict[CharacteristicName, bool]] = {
        CharacteristicName.SUPPORTED_NEW_ALERT_CATEGORY: True,  # required
        CharacteristicName.NEW_ALERT: False,  # optional
        CharacteristicName.SUPPORTED_UNREAD_ALERT_CATEGORY: True,  # required
        CharacteristicName.UNREAD_ALERT_STATUS: False,  # optional
        CharacteristicName.ALERT_NOTIFICATION_CONTROL_POINT: True,  # required
    }
