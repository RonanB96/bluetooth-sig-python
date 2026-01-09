"""Alert Category ID characteristic implementation."""

from __future__ import annotations

from ...types import AlertCategoryID
from .base import BaseCharacteristic
from .templates import EnumTemplate


class AlertCategoryIdCharacteristic(BaseCharacteristic[AlertCategoryID]):
    """Alert Category ID characteristic (0x2A43).

    org.bluetooth.characteristic.alert_category_id

    The Alert Category ID characteristic is used to represent predefined categories of alerts and messages.

    Valid values:
        - 0: Simple Alert
        - 1: Email
        - 2: News
        - 3: Call
        - 4: Missed Call
        - 5: SMS/MMS
        - 6: Voice Mail
        - 7: Schedule
        - 8: High Prioritized Alert
        - 9: Instant Message
        - 10-250: Reserved for Future Use
        - 251-255: Service Specific

    Spec: Bluetooth SIG GATT Specification Supplement, Alert Category ID
    """

    _template = EnumTemplate.uint8(AlertCategoryID)
