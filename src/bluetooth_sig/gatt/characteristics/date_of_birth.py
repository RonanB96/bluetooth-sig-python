"""Date of Birth characteristic (0x2A85)."""

from __future__ import annotations

from ...types import DateData
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser

DateOfBirthData = DateData


class DateOfBirthCharacteristic(BaseCharacteristic[DateOfBirthData]):
    """Date of Birth characteristic (0x2A85).

    org.bluetooth.characteristic.date_of_birth

    Date of Birth characteristic.
    """

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DateOfBirthData:
        """Decode Date of Birth from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (exactly 4 bytes)
            ctx: Optional context for parsing
            validate: Whether to validate ranges (default True)

        Returns:
            DateOfBirthData: Parsed date of birth
        """
        year = DataParser.parse_int16(data, offset=0, signed=False)

        # Month is uint8
        month = data[2]

        # Day is uint8
        day = data[3]

        return DateOfBirthData(year=year, month=month, day=day)

    def _encode_value(self, data: DateOfBirthData) -> bytearray:
        """Encode Date of Birth to raw bytes.

        Args:
            data: DateOfBirthData to encode

        Returns:
            bytearray: Encoded bytes
        """
        result = bytearray()

        # Encode year (uint16, little-endian)
        result.extend(data.year.to_bytes(2, byteorder="little", signed=False))

        # Encode month (uint8)
        result.append(data.month)

        # Encode day (uint8)
        result.append(data.day)

        return result
