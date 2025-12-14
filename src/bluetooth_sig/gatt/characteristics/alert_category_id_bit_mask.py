"""Alert Category ID Bit Mask characteristic implementation."""

from __future__ import annotations

from ...types import AlertCategoryBitMask
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class AlertCategoryIdBitMaskCharacteristic(BaseCharacteristic):
    """Alert Category ID Bit Mask characteristic (0x2A42).

    org.bluetooth.characteristic.alert_category_id_bit_mask

    The Alert Category ID Bit Mask characteristic is used to represent
    support for predefined categories of alerts and messages using a bit mask.

    Structure (2 bytes):
    - Category ID Bit Mask: uint16 (bit field where each bit represents support for a category)
      Bit 0: Simple Alert
      Bit 1: Email
      Bit 2: News
      Bit 3: Call
      Bit 4: Missed Call
      Bit 5: SMS/MMS
      Bit 6: Voice Mail
      Bit 7: Schedule
      Bit 8: High Prioritized Alert
      Bit 9: Instant Message
      Bits 10-15: Reserved for Future Use

    Used by Alert Notification Service (0x1811).

    Spec: Bluetooth SIG GATT Specification Supplement, Alert Category ID Bit Mask
    """

    expected_length: int = 2
    expected_type: type = int

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> AlertCategoryBitMask:
        """Decode Alert Category ID Bit Mask data from bytes.

        Args:
            data: Raw characteristic data (2 bytes)
            ctx: Optional characteristic context

        Returns:
            AlertCategoryBitMask flags

        Raises:
            ValueError: If data is insufficient

        """
        if len(data) < 2:
            raise ValueError(f"Insufficient data for Alert Category ID Bit Mask: expected 2 bytes, got {len(data)}")

        mask_value = DataParser.parse_int16(data, 0, signed=False)
        return AlertCategoryBitMask(mask_value)

    def encode_value(self, data: AlertCategoryBitMask | int) -> bytearray:
        """Encode Alert Category ID Bit Mask data to bytes.

        Args:
            data: AlertCategoryBitMask or int value

        Returns:
            Encoded alert category ID bit mask (2 bytes)

        """
        int_value = int(data) if isinstance(data, AlertCategoryBitMask) else data
        return DataParser.encode_int16(int_value, signed=False)
