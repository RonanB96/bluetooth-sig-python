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

    characteristics: list[CharacteristicInfo] = msgspec.field(default_factory=list)


class ValidationResult(SIGInfo):
    """Result of data validation."""

    is_valid: bool = True
    expected_length: int | None = None
    actual_length: int | None = None
    error_message: str = ""
