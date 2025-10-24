"""Process Tolerances Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class ProcessTolerancesData(msgspec.Struct, frozen=True, kw_only=True):
    """Process Tolerances descriptor data."""

    tolerance_min: int | float
    tolerance_max: int | float


class ProcessTolerancesDescriptor(BaseDescriptor):
    """Process Tolerances Descriptor (0x2914).

    Defines process tolerances for characteristic values.
    Contains minimum and maximum tolerance values.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> ProcessTolerancesData:
        """Parse Process Tolerances descriptor value.

        The format depends on the characteristic's value type.
        For simplicity, this implementation assumes uint16 tolerance values.

        Args:
            data: Raw bytes containing tolerance min and max values

        Returns:
            ProcessTolerancesData with process tolerances

        Raises:
            ValueError: If data length is incorrect
        """
        # Process Tolerances format: tolerance_min + tolerance_max
        # For now, assume 4 bytes total (2 bytes each for uint16)
        if len(data) != 4:
            raise ValueError(f"Process Tolerances data expected 4 bytes, got {len(data)}")

        tolerance_min = DataParser.parse_int16(data, offset=0, endian="little")
        tolerance_max = DataParser.parse_int16(data, offset=2, endian="little")

        return ProcessTolerancesData(
            tolerance_min=tolerance_min,
            tolerance_max=tolerance_max,
        )

    def get_tolerance_min(self, data: bytes) -> int | float:
        """Get the minimum process tolerance."""
        parsed = self._parse_descriptor_value(data)
        return parsed.tolerance_min

    def get_tolerance_max(self, data: bytes) -> int | float:
        """Get the maximum process tolerance."""
        parsed = self._parse_descriptor_value(data)
        return parsed.tolerance_max
