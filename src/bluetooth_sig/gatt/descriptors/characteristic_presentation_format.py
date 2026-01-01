"""Characteristic Presentation Format Descriptor implementation."""

from __future__ import annotations

from enum import IntEnum

import msgspec

from ...registry.core.formattypes import format_types_registry
from ...registry.core.namespace_description import namespace_description_registry
from ...registry.uuids.units import units_registry
from ...types.uuid import BluetoothUUID
from ..characteristics.utils import DataParser
from .base import BaseDescriptor


class FormatNamespace(IntEnum):
    """Format namespace values for Characteristic Presentation Format."""

    UNKNOWN = 0x00
    BLUETOOTH_SIG_ASSIGNED_NUMBERS = 0x01
    RESERVED = 0x02

    @classmethod
    def _missing_(cls, value: object) -> FormatNamespace:
        """Return UNKNOWN for unrecognised namespace values."""
        if not isinstance(value, int):
            return None  # type: ignore[return-value]
        obj = int.__new__(cls, value)
        obj._name_ = f"UNKNOWN_{value}"
        obj._value_ = value
        return obj


class FormatType(IntEnum):
    """Format type values for Characteristic Presentation Format."""

    # Reserved/Unknown
    UNKNOWN = 0x00

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

    @classmethod
    def _missing_(cls, value: object) -> FormatType:
        """Return dynamically created member for unrecognised format values."""
        if not isinstance(value, int):
            return None  # type: ignore[return-value]
        obj = int.__new__(cls, value)
        obj._name_ = f"UNKNOWN_{value}"
        obj._value_ = value
        return obj


class CharacteristicPresentationFormatData(msgspec.Struct, frozen=True, kw_only=True):
    """Characteristic Presentation Format descriptor data.

    Raw integer values are preserved for protocol compatibility.
    Resolved names are provided when available via registry lookups.
    """

    format: FormatType
    """Format type value (e.g., FormatType.UINT16)."""
    format_name: str | None = None
    """Resolved format type name (e.g., 'uint16') from FormatTypesRegistry."""
    exponent: int
    """Base 10 exponent for scaling (-128 to 127)."""
    unit: int
    """Raw unit UUID value (16-bit short form, e.g., 0x272F for Celsius)."""
    unit_name: str | None = None
    """Resolved unit name (e.g., 'degree Celsius') from UnitsRegistry."""
    namespace: FormatNamespace
    """Namespace for description field (e.g., FormatNamespace.BLUETOOTH_SIG_ASSIGNED_NUMBERS)."""
    description: int
    """Description identifier within the namespace."""
    description_name: str | None = None
    """Resolved description name (e.g., 'left', 'first') from NamespaceDescriptionRegistry.

    Only resolved when namespace=0x01 (Bluetooth SIG Assigned Numbers).
    """


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

        format_val = DataParser.parse_int8(data, offset=0)
        namespace_val = DataParser.parse_int8(data, offset=4)
        unit_val = DataParser.parse_int16(data, offset=2, endian="little")
        description_val = DataParser.parse_int16(data, offset=5, endian="little")

        # Resolve format type name from registry
        format_info = format_types_registry.get_format_type_info(format_val)
        format_name = format_info.short_name if format_info else None

        # Resolve unit name from registry (unit is stored as 16-bit UUID)
        unit_uuid = BluetoothUUID(unit_val)
        unit_info = units_registry.get_unit_info(unit_uuid)
        unit_name = unit_info.name if unit_info else None

        # Resolve description name from registry (only for Bluetooth SIG namespace)
        description_name: str | None = None
        if namespace_val == FormatNamespace.BLUETOOTH_SIG_ASSIGNED_NUMBERS:
            description_name = namespace_description_registry.resolve_description_name(description_val)

        return CharacteristicPresentationFormatData(
            format=FormatType(format_val),
            format_name=format_name,
            exponent=DataParser.parse_int8(data, offset=1, signed=True),
            unit=unit_val,
            unit_name=unit_name,
            namespace=FormatNamespace(namespace_val),
            description=description_val,
            description_name=description_name,
        )

    def get_format_type(self, data: bytes) -> FormatType:
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

    def get_namespace(self, data: bytes) -> FormatNamespace:
        """Get the namespace identifier."""
        parsed = self._parse_descriptor_value(data)
        return parsed.namespace

    def get_description(self, data: bytes) -> int:
        """Get the description identifier."""
        parsed = self._parse_descriptor_value(data)
        return parsed.description
