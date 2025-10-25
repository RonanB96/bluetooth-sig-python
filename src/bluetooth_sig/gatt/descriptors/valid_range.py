"""Valid Range Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ValidRangeData(msgspec.Struct, frozen=True, kw_only=True):
    """Valid Range descriptor data."""

    min_value: int | float
    max_value: int | float


class ValidRangeDescriptor(BaseDescriptor):
    """Valid Range Descriptor (0x2906).

    Defines the valid range for characteristic values.
    Contains minimum and maximum values for validation.
    """

    _descriptor_name = "Valid Range"

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> ValidRangeData:
        """Parse Valid Range descriptor value.

        The format depends on the characteristic's value type.
        For simplicity, this implementation assumes uint16 min/max values.
        In practice, this should be adapted based on the characteristic's format.

        Args:
            data: Raw bytes containing min and max values

        Returns:
            ValidRangeData with min and max values

        Raises:
            ValueError: If data length is incorrect
        """
        # Valid Range format: min_value (same format as characteristic) + max_value
        # For now, assume 4 bytes total (2 bytes min + 2 bytes max for uint16)
        if len(data) != 4:
            raise ValueError(f"Valid Range data expected 4 bytes, got {len(data)}")

        min_value = DataParser.parse_int16(data, offset=0, endian="little")
        max_value = DataParser.parse_int16(data, offset=2, endian="little")

        return ValidRangeData(
            min_value=min_value,
            max_value=max_value,
        )

    def get_min_value(self, data: bytes) -> int | float:
        """Get the minimum valid value.

        Args:
            data: Raw descriptor data

        Returns:
            Minimum valid value for the characteristic
        """
        parsed = self._parse_descriptor_value(data)
        return parsed.min_value

    def get_max_value(self, data: bytes) -> int | float:
        """Get the maximum valid value.

        Args:
            data: Raw descriptor data

        Returns:
            Maximum valid value for the characteristic
        """
        parsed = self._parse_descriptor_value(data)
        return parsed.max_value

    def is_value_in_range(self, data: bytes, value: int | float) -> bool:
        """Check if a value is within the valid range.

        Args:
            data: Raw descriptor data
            value: Value to check

        Returns:
            True if value is within [min_value, max_value] range
        """
        parsed = self._parse_descriptor_value(data)
        return parsed.min_value <= value <= parsed.max_value
