"""Characteristic Aggregate Format Descriptor implementation."""

from __future__ import annotations

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class CharacteristicAggregateFormatData(msgspec.Struct, frozen=True, kw_only=True):
    """Characteristic Aggregate Format descriptor data."""

    attribute_handles: list[int]


class CharacteristicAggregateFormatDescriptor(BaseDescriptor):
    """Characteristic Aggregate Format Descriptor (0x2905).

    Contains a list of attribute handles that collectively form an aggregate value.
    Used to group multiple characteristics into a single logical value.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16[]"

    def _parse_descriptor_value(self, data: bytes) -> CharacteristicAggregateFormatData:
        """Parse Characteristic Aggregate Format value.

        Contains a list of 16-bit attribute handles (little-endian).
        The number of handles is determined by data length / 2.

        Args:
            data: Raw bytes containing attribute handles

        Returns:
            CharacteristicAggregateFormatData with list of handles

        Raises:
            ValueError: If data length is not even (handles are 2 bytes each)
        """
        if len(data) % 2 != 0:
            raise ValueError(f"Characteristic Aggregate Format data must have even length, got {len(data)}")

        if len(data) == 0:
            return CharacteristicAggregateFormatData(attribute_handles=[])

        handles: list[int] = []
        for i in range(0, len(data), 2):
            handle = DataParser.parse_int16(data, offset=i, endian="little")
            handles.append(handle)

        return CharacteristicAggregateFormatData(attribute_handles=handles)

    def get_attribute_handles(self, data: bytes) -> list[int]:
        """Get the list of attribute handles."""
        parsed = self._parse_descriptor_value(data)
        return parsed.attribute_handles

    def get_handle_count(self, data: bytes) -> int:
        """Get the number of attribute handles."""
        return len(self.get_attribute_handles(data))
