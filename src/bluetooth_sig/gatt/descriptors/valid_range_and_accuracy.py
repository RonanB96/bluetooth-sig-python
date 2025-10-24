"""Valid Range and Accuracy Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ValidRangeAndAccuracyData(msgspec.Struct, frozen=True, kw_only=True):
    """Valid Range and Accuracy descriptor data."""

    min_value: int | float
    max_value: int | float
    accuracy: int | float


class ValidRangeAndAccuracyDescriptor(BaseDescriptor):
    """Valid Range and Accuracy Descriptor (0x2911).

    Defines the valid range and accuracy for characteristic values.
    Contains minimum value, maximum value, and accuracy information.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> ValidRangeAndAccuracyData:
        """Parse Valid Range and Accuracy descriptor value.

        The format depends on the characteristic's value type.
        For simplicity, this implementation assumes uint16 values.

        Args:
            data: Raw bytes containing min, max, and accuracy values

        Returns:
            ValidRangeAndAccuracyData with range and accuracy info

        Raises:
            ValueError: If data length is incorrect
        """
        # Valid Range and Accuracy format: min_value + max_value + accuracy
        # For now, assume 6 bytes total (2 bytes each for uint16)
        if len(data) != 6:
            raise ValueError(f"Valid Range and Accuracy data expected 6 bytes, got {len(data)}")

        min_value = DataParser.parse_int16(data, offset=0, endian="little")
        max_value = DataParser.parse_int16(data, offset=2, endian="little")
        accuracy = DataParser.parse_int16(data, offset=4, endian="little")

        return ValidRangeAndAccuracyData(
            min_value=min_value,
            max_value=max_value,
            accuracy=accuracy,
        )

    def get_min_value(self, data: bytes) -> int | float:
        """Get the minimum valid value."""
        parsed = self._parse_descriptor_value(data)
        return parsed.min_value

    def get_max_value(self, data: bytes) -> int | float:
        """Get the maximum valid value."""
        parsed = self._parse_descriptor_value(data)
        return parsed.max_value

    def get_accuracy(self, data: bytes) -> int | float:
        """Get the accuracy value."""
        parsed = self._parse_descriptor_value(data)
        return parsed.accuracy

    def is_value_in_range(self, data: bytes, value: int | float) -> bool:
        """Check if a value is within the valid range."""
        parsed = self._parse_descriptor_value(data)
        return parsed.min_value <= value <= parsed.max_value
