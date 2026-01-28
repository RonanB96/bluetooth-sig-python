"""Manufacturer Limits Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ManufacturerLimitsData(msgspec.Struct, frozen=True, kw_only=True):
    """Manufacturer Limits descriptor data."""

    min_limit: int | float
    max_limit: int | float


class ManufacturerLimitsDescriptor(BaseDescriptor):
    """Manufacturer Limits Descriptor (0x2913).

    Defines manufacturer-specified limits for characteristic values.
    Contains minimum and maximum limits set by the manufacturer.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> ManufacturerLimitsData:
        """Parse Manufacturer Limits descriptor value.

        The format depends on the characteristic's value type.
        For simplicity, this implementation assumes uint16 min/max values.

        Args:
            data: Raw bytes containing min and max limit values

        Returns:
            ManufacturerLimitsData with manufacturer limits

        Raises:
            ValueError: If data length is incorrect
        """
        # Manufacturer Limits format: min_limit + max_limit
        # For now, assume 4 bytes total (2 bytes each for uint16)

        min_limit = DataParser.parse_int16(data, offset=0, endian="little")
        max_limit = DataParser.parse_int16(data, offset=2, endian="little")

        return ManufacturerLimitsData(
            min_limit=min_limit,
            max_limit=max_limit,
        )

    def get_min_limit(self, data: bytes) -> int | float:
        """Get the minimum manufacturer limit."""
        parsed = self._parse_descriptor_value(data)
        return parsed.min_limit

    def get_max_limit(self, data: bytes) -> int | float:
        """Get the maximum manufacturer limit."""
        parsed = self._parse_descriptor_value(data)
        return parsed.max_limit

    def is_value_within_limits(self, data: bytes, value: float) -> bool:
        """Check if a value is within manufacturer limits."""
        parsed = self._parse_descriptor_value(data)
        return parsed.min_limit <= value <= parsed.max_limit
