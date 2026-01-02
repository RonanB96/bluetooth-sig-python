"""Alert Level characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from .base import BaseCharacteristic
from .templates import EnumTemplate


class AlertLevel(IntEnum):
    """Alert level values as defined by Bluetooth SIG.

    Values:
        NO_ALERT: No alert (0x00)
        MILD_ALERT: Mild alert (0x01)
        HIGH_ALERT: High alert (0x02)
    """

    NO_ALERT = 0x00
    MILD_ALERT = 0x01
    HIGH_ALERT = 0x02


class AlertLevelCharacteristic(BaseCharacteristic):
    """Alert Level characteristic (0x2A06).

    org.bluetooth.characteristic.alert_level

    The Alert Level characteristic defines the level of alert and is
    used by services such as Immediate Alert (0x1802), Link Loss (0x1803),
    and Phone Alert Status (0x180E).

    Valid values:
        - 0x00: No Alert
        - 0x01: Mild Alert
        - 0x02: High Alert
        - 0x03-0xFF: Reserved for Future Use

    Spec: Bluetooth SIG GATT Specification Supplement, Alert Level
    """

    _template = EnumTemplate.uint8(AlertLevel)

    # YAML has no range constraint; enforce valid enum bounds.
    min_value: int = AlertLevel.NO_ALERT  # 0
    max_value: int = AlertLevel.HIGH_ALERT  # 2
