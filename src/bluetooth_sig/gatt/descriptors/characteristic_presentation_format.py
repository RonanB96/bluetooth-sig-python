"""Characteristic Presentation Format Descriptor implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class FormatNamespace(IntEnum):
    """Format namespace values for Characteristic Presentation Format."""

    BLUETOOTH_SIG_ASSIGNED_NUMBERS = 0x01
    RESERVED = 0x02


class FormatType(IntEnum):
    """Format type values for Characteristic Presentation Format."""

    # Common Bluetooth SIG format types
    BOOLEAN = 0x01
    UINT2 = 0x02
    UINT4 = 0x03
    UINT8 = 0x04
    UINT12 = 0x05
    UINT16 = 0x06
    UINT24 = 0x07
    UINT32 = 0x08
    UINT48 = 0x09
    UINT64 = 0x0A
    UINT128 = 0x0B
    SINT8 = 0x0C
    SINT12 = 0x0D
    SINT16 = 0x0E
    SINT24 = 0x0F
    SINT32 = 0x10
    SINT48 = 0x11
    SINT64 = 0x12
    SINT128 = 0x13
    FLOAT32 = 0x14
    FLOAT64 = 0x15
    SFLOAT = 0x16
    FLOAT = 0x17
    DUINT16 = 0x18
    UTF8S = 0x19
    UTF16S = 0x1A
    STRUCT = 0x1B


class CharacteristicPresentationFormatData(msgspec.Struct, frozen=True, kw_only=True):
    """Characteristic Presentation Format descriptor data."""

    format: int
    exponent: int
    unit: int
    namespace: int
    description: int


class CharacteristicPresentationFormatDescriptor(BaseDescriptor):
    """Characteristic Presentation Format Descriptor (0x2904).

    Describes how characteristic values should be presented to users.
    Contains format, exponent, unit, namespace, and description information.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "struct"

    def _parse_descriptor_value(self, data: bytes) -> CharacteristicPresentationFormatData:
        """Parse Characteristic Presentation Format value.

        Format: 7 bytes
        - Format (1 byte): Data type format
        - Exponent (1 byte): Base 10 exponent (-128 to 127)
        - Unit (2 bytes): Unit of measurement (little-endian)
        - Namespace (1 byte): Namespace for description
        - Description (2 bytes): Description identifier (little-endian)

        Args:
            data: Raw bytes (should be 7 bytes)

        Returns:
            CharacteristicPresentationFormatData with format information

        Raises:
            ValueError: If data is not exactly 7 bytes
        """
        if len(data) != 7:
            raise ValueError(f"Characteristic Presentation Format data must be exactly 7 bytes, got {len(data)}")

        return CharacteristicPresentationFormatData(
            format=DataParser.parse_int8(data, offset=0),
            exponent=DataParser.parse_int8(data, offset=1, signed=True),
            unit=DataParser.parse_int16(data, offset=2, endian="little"),
            namespace=DataParser.parse_int8(data, offset=4),
            description=DataParser.parse_int16(data, offset=5, endian="little"),
        )

    def get_format_type(self, data: bytes) -> int:
        """Get the format type."""
        parsed = self._parse_descriptor_value(data)
        return parsed.format

    def get_exponent(self, data: bytes) -> int:
        """Get the exponent for scaling."""
        parsed = self._parse_descriptor_value(data)
        return parsed.exponent

    def get_unit(self, data: bytes) -> int:
        """Get the unit identifier."""
        parsed = self._parse_descriptor_value(data)
        return parsed.unit

    def get_namespace(self, data: bytes) -> int:
        """Get the namespace identifier."""
        parsed = self._parse_descriptor_value(data)
        return parsed.namespace

    def get_description(self, data: bytes) -> int:
        """Get the description identifier."""
        parsed = self._parse_descriptor_value(data)
        return parsed.description
