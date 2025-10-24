"""Number of Digitals Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class NumberOfDigitalsData(msgspec.Struct, frozen=True, kw_only=True):
    """Number of Digitals descriptor data."""

    number_of_digitals: int


class NumberOfDigitalsDescriptor(BaseDescriptor):
    """Number of Digitals Descriptor (0x2909).

    Specifies the number of digital states supported by a characteristic.
    Used in sensor applications.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint8"

    def _parse_descriptor_value(self, data: bytes) -> NumberOfDigitalsData:
        """Parse Number of Digitals value.

        Args:
            data: Raw bytes (should be 1 byte for uint8)

        Returns:
            NumberOfDigitalsData with number of digitals

        Raises:
            ValueError: If data is not exactly 1 byte
        """
        if len(data) != 1:
            raise ValueError(f"Number of Digitals data must be exactly 1 byte, got {len(data)}")

        number_of_digitals = DataParser.parse_int8(data)

        return NumberOfDigitalsData(number_of_digitals=number_of_digitals)

    def get_number_of_digitals(self, data: bytes) -> int:
        """Get the number of digitals."""
        parsed = self._parse_descriptor_value(data)
        return parsed.number_of_digitals
