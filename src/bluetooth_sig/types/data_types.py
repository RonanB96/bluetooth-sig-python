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


class ValidationAccumulator:
    """Result of characteristic data validation with error/warning accumulation.

    Used during parsing to accumulate validation issues from multiple validation steps.
    Provides methods to add errors/warnings and check overall validity.
    """

    def __init__(self) -> None:
        """Initialize empty validation result."""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str) -> None:
        """Add a validation error message.

        Args:
            message: Error message to add
        """
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a validation warning message.

        Args:
            message: Warning message to add
        """
        self.warnings.append(message)

    @property
    def valid(self) -> bool:
        """Check if validation passed (no errors).

        Returns:
            True if no errors, False otherwise
        """
        return len(self.errors) == 0


class ValidationResult(msgspec.Struct, frozen=True, kw_only=True):
    """Summary of validation results for external API consumption.

    Lightweight validation result for API responses, not for accumulation.
    """

    is_valid: bool
    actual_length: int
    expected_length: int | None = None
    error_message: str = ""
