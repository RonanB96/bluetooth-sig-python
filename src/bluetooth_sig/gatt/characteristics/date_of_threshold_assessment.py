"""Date of Threshold Assessment characteristic (0x2A86)."""

from __future__ import annotations

from ...types import DateData
from ..constants import MAX_YEAR_VALUE
from ..context import CharacteristicContext
from ..exceptions import ValueRangeError
from .base import BaseCharacteristic
from .utils import DataParser
from .utils.ieee11073_parser import IEEE11073Parser

DateOfThresholdAssessmentData = DateData


class DateOfThresholdAssessmentCharacteristic(BaseCharacteristic[DateOfThresholdAssessmentData]):
    """Date of Threshold Assessment characteristic (0x2A86).

    org.bluetooth.characteristic.date_of_threshold_assessment

    Date of Threshold Assessment characteristic.
    """

    expected_length: int = 4  # Year(2) + Month(1) + Day(1)
    min_length: int = 4
    max_length: int = 4

    def _decode_value(
        self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
    ) -> DateOfThresholdAssessmentData:
        """Decode Date of Threshold Assessment from raw bytes.

        Args:
            data: Raw bytes from BLE characteristic (4 bytes)
            ctx: Optional context for parsing
            validate: Whether to validate ranges (default True)

        Returns:
            DateOfThresholdAssessmentData with year, month, day

        Raises:
            InsufficientDataError: If data length is not exactly 4 bytes
        """
        year = DataParser.parse_int16(data, 0, signed=False)

        # Month is uint8
        month = data[2]

        # Day is uint8
        day = data[3]

        return DateOfThresholdAssessmentData(year=year, month=month, day=day)

    def _encode_value(self, data: DateOfThresholdAssessmentData) -> bytearray:
        """Encode Date of Threshold Assessment to bytes.

        Args:
            data: DateOfThresholdAssessmentData to encode

        Returns:
            Encoded bytes (4 bytes)

        Raises:
            ValueRangeError: If year, month, or day are out of valid range
        """
        # Validate year
        if not ((data.year == 0) or (IEEE11073Parser.IEEE11073_MIN_YEAR <= data.year <= MAX_YEAR_VALUE)):
            raise ValueRangeError("year", data.year, IEEE11073Parser.IEEE11073_MIN_YEAR, MAX_YEAR_VALUE)

        # Validate month
        if not ((data.month == 0) or (IEEE11073Parser.MONTH_MIN <= data.month <= IEEE11073Parser.MONTH_MAX)):
            raise ValueRangeError("month", data.month, IEEE11073Parser.MONTH_MIN, IEEE11073Parser.MONTH_MAX)

        # Validate day
        if not ((data.day == 0) or (IEEE11073Parser.DAY_MIN <= data.day <= IEEE11073Parser.DAY_MAX)):
            raise ValueRangeError("day", data.day, IEEE11073Parser.DAY_MIN, IEEE11073Parser.DAY_MAX)

        result = bytearray()

        # Encode year (uint16, little-endian)
        result.extend(DataParser.encode_int16(data.year, signed=False))

        # Encode month (uint8)
        result.append(data.month)

        # Encode day (uint8)
        result.append(data.day)

        return result
