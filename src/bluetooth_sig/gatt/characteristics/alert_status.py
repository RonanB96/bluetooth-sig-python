"""Alert Status characteristic implementation."""

from __future__ import annotations

import msgspec

from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AlertStatusData(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Alert Status characteristic."""

    ringer_state: bool
    vibrate_state: bool
    display_alert_status: bool


class AlertStatusCharacteristic(BaseCharacteristic[AlertStatusData]):
    """Alert Status characteristic (0x2A3F).

    org.bluetooth.characteristic.alert_status

    The Alert Status characteristic defines the Status of alert.
    Bit 0: Ringer State (0=not active, 1=active)
    Bit 1: Vibrate State (0=not active, 1=active)
    Bit 2: Display Alert Status (0=not active, 1=active)
    Bits 3-7: Reserved for future use
    """

    expected_length: int = 1
    min_length: int = 1

    # Bit masks for alert status flags
    RINGER_STATE_MASK = 0x01  # Bit 0
    VIBRATE_STATE_MASK = 0x02  # Bit 1
    DISPLAY_ALERT_STATUS_MASK = 0x04  # Bit 2

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> AlertStatusData:
        """Parse alert status data according to Bluetooth specification.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional CharacteristicContext (unused)
            validate: Whether to validate ranges (default True)

        Returns:
            AlertStatusData containing parsed alert status flags.

        Raises:
            ValueError: If data format is invalid.

        """
        status_byte = DataParser.parse_int8(data, 0, signed=False)

        # Extract bit fields according to specification
        ringer_state = bool(status_byte & self.RINGER_STATE_MASK)
        vibrate_state = bool(status_byte & self.VIBRATE_STATE_MASK)
        display_alert_status = bool(status_byte & self.DISPLAY_ALERT_STATUS_MASK)

        return AlertStatusData(
            ringer_state=ringer_state,
            vibrate_state=vibrate_state,
            display_alert_status=display_alert_status,
        )

    def _encode_value(self, data: AlertStatusData) -> bytearray:
        """Encode AlertStatusData back to bytes.

        Args:
            data: AlertStatusData instance to encode

        validate: Whether to validate ranges (default True)

        Returns:
            Encoded bytes representing the alert status

        """
        status_byte = 0
        if data.ringer_state:
            status_byte |= self.RINGER_STATE_MASK
        if data.vibrate_state:
            status_byte |= self.VIBRATE_STATE_MASK
        if data.display_alert_status:
            status_byte |= self.DISPLAY_ALERT_STATUS_MASK

        return bytearray([status_byte])
