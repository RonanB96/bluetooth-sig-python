"""Alert Level characteristic implementation."""

from __future__ import annotations

from enum import IntEnum

from bluetooth_sig.types.context import CharacteristicContext

from .base import BaseCharacteristic
from .templates import Uint8Template


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

    _template = Uint8Template()

    # YAML has no range constraint; enforce valid enum bounds.
    min_value: int = AlertLevel.NO_ALERT  # 0
    max_value: int = AlertLevel.HIGH_ALERT  # 2

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> AlertLevel:
        """Decode alert level from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            AlertLevel enum value

        Raises:
            ValueError: If data is less than 1 byte or value is invalid

        """
        raw_value = self._template.decode_value(data, offset=0, ctx=ctx)

        # Validate against known values
        if raw_value not in (AlertLevel.NO_ALERT, AlertLevel.MILD_ALERT, AlertLevel.HIGH_ALERT):
            raise ValueError(
                f"Alert Level value {raw_value} is reserved or invalid. "
                f"Valid values: 0 (No Alert), 1 (Mild Alert), 2 (High Alert)"
            )

        return AlertLevel(raw_value)

    def encode_value(self, data: AlertLevel | int) -> bytearray:
        r"""Encode alert level to raw bytes.

        Args:
            data: AlertLevel enum value or integer (0-2)

        Returns:
            Encoded characteristic data (1 byte)

        Raises:
            ValueError: If data is not 0, 1, or 2

        """
        # Convert AlertLevel to int if needed
        int_value = int(data) if isinstance(data, AlertLevel) else data

        # Validate range
        if int_value not in (AlertLevel.NO_ALERT, AlertLevel.MILD_ALERT, AlertLevel.HIGH_ALERT):
            raise ValueError(
                f"Alert Level value {int_value} is invalid. Valid values: 0 (No Alert), 1 (Mild Alert), 2 (High Alert)"
            )

        return self._template.encode_value(int_value)
