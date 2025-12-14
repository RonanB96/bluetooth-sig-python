"""Alert Category ID characteristic implementation."""

from __future__ import annotations

from ...types import AlertCategoryID, validate_category_id
from ..constants import UINT8_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .templates import Uint8Template


class AlertCategoryIdCharacteristic(BaseCharacteristic):
    """Alert Category ID characteristic (0x2A43).

    org.bluetooth.characteristic.alert_category_id

    The Alert Category ID characteristic is used to represent predefined categories of alerts and messages.
    The structure of this characteristic is defined below.

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

    # Validation attributes
    expected_length: int = 1  # uint8
    min_value: int = 0
    max_value: int = UINT8_MAX
    expected_type: type = int

    _template = Uint8Template()

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> AlertCategoryID:
        """Decode alert category ID from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (1 byte)
            ctx: Optional context for parsing

        Returns:
            AlertCategoryID enum value

        Raises:
            ValueError: If data is less than 1 byte or value is invalid

        """
        raw_value = self._template.decode_value(data, offset=0, ctx=ctx)

        # Validate against known values using the existing validation function
        return validate_category_id(raw_value)

    def encode_value(self, data: AlertCategoryID | int) -> bytearray:
        """Encode alert category ID to raw bytes.

        Args:
            data: AlertCategoryID enum value or integer

        Returns:
            Encoded characteristic data (1 byte)

        Raises:
            ValueError: If data is not a valid category ID

        """
        # Convert AlertCategoryID to int if needed
        int_value = int(data) if isinstance(data, AlertCategoryID) else data

        # Validate the value
        validate_category_id(int_value)

        return self._template.encode_value(int_value)
