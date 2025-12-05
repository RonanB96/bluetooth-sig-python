"""Data types for Bluetooth SIG standards."""

from __future__ import annotations

import msgspec

from .base_types import SIGInfo
from .gatt_enums import ValueType


class ParseFieldError(msgspec.Struct, frozen=True, kw_only=True):
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


class DateData(msgspec.Struct, frozen=True, kw_only=True):
    """Shared data type for date values with year, month, and day fields."""

    year: int
    month: int
    day: int


class CharacteristicInfo(SIGInfo):
    """Information about a Bluetooth characteristic from SIG/YAML specifications.

    This contains only static metadata resolved from YAML or SIG specs.
    Runtime properties (read/write/notify capabilities) are stored separately
    on the BaseCharacteristic instance as they're discovered from the actual device.
    """

    value_type: ValueType = ValueType.UNKNOWN
    unit: str = ""


class ServiceInfo(SIGInfo):
    """Information about a Bluetooth service."""

    characteristics: list[CharacteristicInfo] = msgspec.field(default_factory=list[CharacteristicInfo])


class ValidationResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result of characteristic data validation.

    Provides diagnostic information about whether characteristic data
    matches the expected format per Bluetooth SIG specifications.

    This is a lightweight validation result, NOT SIG registry metadata.
    For characteristic metadata (uuid, name, description), query the
    characteristic's info directly.

    Attributes:
        is_valid: Whether the data format is valid per SIG specs
        actual_length: Number of bytes in the data
        expected_length: Expected bytes for fixed-length characteristics, None for variable
        error_message: Description of validation failure, empty string if valid
    """

    is_valid: bool
    actual_length: int
    expected_length: int | None = None
    error_message: str = ""
