"""Characteristic Extended Properties Descriptor implementation."""

from __future__ import annotations

from enum import IntFlag

import msgspec

from ..characteristics.utils import DataParser
from ..constants import SIZE_UINT16
from .base import BaseDescriptor


class ExtendedPropertiesFlags(IntFlag):
    """Characteristic Extended Properties flags."""

    RELIABLE_WRITE = 0x0001
    WRITABLE_AUXILIARIES = 0x0002


class CharacteristicExtendedPropertiesData(msgspec.Struct, frozen=True, kw_only=True):
    """Characteristic Extended Properties descriptor data."""

    reliable_write: bool
    writable_auxiliaries: bool


class CharacteristicExtendedPropertiesDescriptor(BaseDescriptor):
    """Characteristic Extended Properties Descriptor (0x2900).

    Defines extended properties for a characteristic using bit flags.
    Indicates support for reliable writes and writable auxiliaries.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "uint16"

    def _parse_descriptor_value(self, data: bytes) -> CharacteristicExtendedPropertiesData:
        """Parse Characteristic Extended Properties value.

        Args:
            data: Raw bytes (should be 2 bytes for uint16)

        Returns:
            CharacteristicExtendedPropertiesData with property flags

        Raises:
            ValueError: If data is not exactly 2 bytes
        """
        if len(data) != SIZE_UINT16:
            raise ValueError(f"Characteristic Extended Properties data must be exactly 2 bytes, got {len(data)}")

        # Parse as little-endian uint16
        value = DataParser.parse_int16(data, endian="little")

        return CharacteristicExtendedPropertiesData(
            reliable_write=bool(value & ExtendedPropertiesFlags.RELIABLE_WRITE),
            writable_auxiliaries=bool(value & ExtendedPropertiesFlags.WRITABLE_AUXILIARIES),
        )

    def supports_reliable_write(self, data: bytes) -> bool:
        """Check if reliable write is supported."""
        parsed = self._parse_descriptor_value(data)
        return parsed.reliable_write

    def supports_writable_auxiliaries(self, data: bytes) -> bool:
        """Check if writable auxiliaries are supported."""
        parsed = self._parse_descriptor_value(data)
        return parsed.writable_auxiliaries
