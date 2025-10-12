"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from .context import CharacteristicContext
from .gatt_enums import GattProperty, ValueType
from .uuid import BluetoothUUID


@dataclass(frozen=True)
class ParseFieldError:
    """Represents a field-level parsing error with diagnostic information.

    This provides structured error information similar to Pydantic's validation
    errors, making it easier to debug which specific field failed and why.

    Attributes:
        field: Name of the field that failed (e.g., "temperature", "flags")
        reason: Human-readable description of why parsing failed
        offset: Optional byte offset where the field starts in raw data
        raw_slice: Optional raw bytes that were being parsed when error occurred
    """

    field: str
    reason: str
    offset: int | None = None
    raw_slice: bytes | None = None


@dataclass
class SIGInfo:
    """Base information about Bluetooth SIG characteristics or services."""

    uuid: BluetoothUUID
    name: str
    description: str = ""


@dataclass
class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic."""

    value_type: ValueType = ValueType.UNKNOWN
    unit: str = ""
    properties: list[GattProperty] = field(default_factory=lambda: cast(list[GattProperty], []))


@dataclass
class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""

    characteristics: list[CharacteristicInfo] = field(default_factory=lambda: cast(list[CharacteristicInfo], []))


@dataclass
class CharacteristicData:  # pylint: disable=too-many-instance-attributes
    """Parsed characteristic data with validation results.

    Provides structured error reporting with field-level diagnostics and parse traces
    to help identify exactly where and why parsing failed.

    NOTE: This dataclass intentionally has more attributes than the standard limit
    to provide complete diagnostic information. The additional fields (field_errors,
    parse_trace) are essential for actionable error reporting and debugging.
    """

    info: CharacteristicInfo
    value: Any | None = None
    raw_data: bytes = b""
    parse_success: bool = False
    error_message: str = ""
    source_context: CharacteristicContext = field(default_factory=CharacteristicContext)
    field_errors: list[ParseFieldError] = field(default_factory=list)
    parse_trace: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Get the characteristic name from info."""
        return self.info.name

    @property
    def properties(self) -> list[GattProperty]:
        """Get the properties as strings for protocol compatibility."""
        return self.info.properties

    @property
    def uuid(self) -> BluetoothUUID:
        """Get the characteristic UUID from info."""
        return self.info.uuid

    @property
    def unit(self) -> str:
        """Get the characteristic unit from info."""
        return self.info.unit


@dataclass
class ValidationResult(SIGInfo):
    """Result of data validation."""

    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str = ""


@dataclass
class CharacteristicRegistration:
    """Unified metadata for custom UUID registration"""

    uuid: BluetoothUUID
    name: str = ""
    id: str | None = None
    summary: str = ""
    unit: str = ""
    value_type: ValueType = ValueType.STRING


@dataclass
class ServiceRegistration:
    """Unified metadata for custom UUID registration"""

    uuid: BluetoothUUID
    name: str = ""
    id: str | None = None
    summary: str = ""
