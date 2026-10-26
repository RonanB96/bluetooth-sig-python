"""IMD Status characteristic (0x2C0C).

Reports current status flags and additional status data from an
Industrial Monitoring Device.

References:
    Bluetooth SIG Industrial Monitoring Device Service
"""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ...types.gatt_enums import CharacteristicRole
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser


class IMDStatusFlags(IntFlag):
    """IMD Status flags (uint8)."""

    DEVICE_OPERATING = 0x01
    ALARM_ACTIVE = 0x02
    WARNING_ACTIVE = 0x04
    MAINTENANCE_REQUIRED = 0x08
    BATTERY_LOW = 0x10
    COMMUNICATION_ERROR = 0x20


class IMDStatusData(msgspec.Struct, frozen=True, kw_only=True):
    """Parsed data from IMD Status characteristic.

    Attributes:
        flags: IMD status flags.
        additional_data: Raw additional status bytes.
    """

    flags: IMDStatusFlags
    additional_data: bytes = b""


class IMDStatusCharacteristic(BaseCharacteristic[IMDStatusData]):
    """IMD Status characteristic (0x2C0C).

    org.bluetooth.characteristic.imd_status

    Reports current status from an Industrial Monitoring Device.
    """

    _manual_role = CharacteristicRole.STATUS
    min_length = 1
    allow_variable_length = True

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> IMDStatusData:
        """Parse IMD Status data.

        Format: Flags (uint8) + AdditionalData (variable).
        """
        flags = IMDStatusFlags(DataParser.parse_int8(data, 0, signed=False))
        additional_data = bytes(data[1:])

        return IMDStatusData(
            flags=flags,
            additional_data=additional_data,
        )

    def _encode_value(self, data: IMDStatusData) -> bytearray:
        """Encode IMD Status data."""
        result = bytearray()
        result.extend(DataParser.encode_int8(int(data.flags), signed=False))
        result.extend(data.additional_data)
        return result
