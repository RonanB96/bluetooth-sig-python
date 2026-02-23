"""Validation logic for characteristic values.

Provides range, type, and length validation with a three-level precedence
system: descriptor Valid Range > class-level attributes > YAML-derived ranges.
"""

from __future__ import annotations

from typing import Any

from ....types import SpecialValueResult
from ....types.data_types import ValidationAccumulator
from ....types.registry import CharacteristicSpec
from ...context import CharacteristicContext
from ...descriptor_utils import get_valid_range_from_context as _get_valid_range


class CharacteristicValidator:
    """Validates characteristic values against range, type, and length constraints.

    Uses a back-reference to the owning characteristic to access validation
    attributes (``min_value``, ``max_value``, ``expected_length``, etc.) and
    YAML-derived metadata.  This class is an **internal** implementation detail
    of ``BaseCharacteristic`` and should not be used directly.
    """

    def __init__(self, char: Any) -> None:  # noqa: ANN401  # Avoids circular BaseCharacteristic import
        """Initialise with a back-reference to the owning characteristic.

        Args:
            char: BaseCharacteristic instance (typed as Any to avoid circular import)

        """
        self._char = char

    # ------------------------------------------------------------------
    # Range validation
    # ------------------------------------------------------------------

    def validate_range(  # pylint: disable=too-many-branches
        self,
        value: Any,  # noqa: ANN401  # Validates values of various numeric types
        ctx: CharacteristicContext | None = None,
    ) -> ValidationAccumulator:
        """Validate value is within min/max range.

        Validation precedence:
            1. Descriptor Valid Range (if present in context) — most specific, device-reported
            2. Class-level validation attributes (min_value, max_value) — characteristic spec defaults
            3. YAML-derived value range from structure — Bluetooth SIG specification

        Args:
            value: The value to validate.
            ctx: Optional characteristic context containing descriptors.

        Returns:
            ValidationAccumulator with errors if validation fails.

        """
        char = self._char
        result = ValidationAccumulator()

        # Skip validation for SpecialValueResult
        if isinstance(value, SpecialValueResult):
            return result

        # Skip validation for non-numeric types
        if not isinstance(value, (int, float)):
            return result

        # Check descriptor Valid Range first (takes precedence over class attributes)
        descriptor_range = _get_valid_range(ctx) if ctx else None
        if descriptor_range is not None:
            min_val, max_val = descriptor_range
            if value < min_val or value > max_val:
                error_msg = (
                    f"Value {value} is outside valid range [{min_val}, {max_val}] "
                    f"(source: Valid Range descriptor for {char.name})"
                )
                if char.unit:
                    error_msg += f" [unit: {char.unit}]"
                result.add_error(error_msg)
            # Descriptor validation checked — skip class-level checks
            return result

        # Fall back to class-level validation attributes
        if char.min_value is not None and value < char.min_value:
            error_msg = (
                f"Value {value} is below minimum {char.min_value} "
                f"(source: class-level constraint for {char.__class__.__name__})"
            )
            if char.unit:
                error_msg += f" [unit: {char.unit}]"
            result.add_error(error_msg)
        if char.max_value is not None and value > char.max_value:
            error_msg = (
                f"Value {value} is above maximum {char.max_value} "
                f"(source: class-level constraint for {char.__class__.__name__})"
            )
            if char.unit:
                error_msg += f" [unit: {char.unit}]"
            result.add_error(error_msg)

        # Fall back to YAML-derived value range from structure
        _validate_yaml_range(result, value, char)

        return result

    # ------------------------------------------------------------------
    # Type validation
    # ------------------------------------------------------------------

    def validate_type(self, value: Any) -> ValidationAccumulator:  # noqa: ANN401
        """Validate value type matches expected_type if specified.

        Args:
            value: The value to validate.

        Returns:
            ValidationAccumulator with errors if validation fails.

        """
        result = ValidationAccumulator()

        expected_type: type | None = self._char.expected_type
        if expected_type is not None and not isinstance(value, (expected_type, SpecialValueResult)):
            error_msg = (
                f"Type validation failed for {self._char.name}: "
                f"expected {expected_type.__name__}, got {type(value).__name__} "
                f"(value: {value})"
            )
            result.add_error(error_msg)
        return result

    # ------------------------------------------------------------------
    # Length validation
    # ------------------------------------------------------------------

    def validate_length(self, data: bytes | bytearray) -> ValidationAccumulator:
        """Validate data length meets requirements.

        Args:
            data: The data to validate.

        Returns:
            ValidationAccumulator with errors if validation fails.

        """
        char = self._char
        result = ValidationAccumulator()
        length = len(data)

        # Determine validation source for error context
        yaml_size = char.get_yaml_field_size()
        source_context = ""
        if yaml_size is not None:
            source_context = f" (YAML specification: {yaml_size} bytes)"
        elif char.expected_length is not None or char.min_length is not None or char.max_length is not None:
            source_context = f" (class-level constraint for {char.__class__.__name__})"

        if char.expected_length is not None and length != char.expected_length:
            error_msg = (
                f"Length validation failed for {char.name}: "
                f"expected exactly {char.expected_length} bytes, got {length}{source_context}"
            )
            result.add_error(error_msg)
        if char.min_length is not None and length < char.min_length:
            error_msg = (
                f"Length validation failed for {char.name}: "
                f"expected at least {char.min_length} bytes, got {length}{source_context}"
            )
            result.add_error(error_msg)
        if char.max_length is not None and length > char.max_length:
            error_msg = (
                f"Length validation failed for {char.name}: "
                f"expected at most {char.max_length} bytes, got {length}{source_context}"
            )
            result.add_error(error_msg)
        return result


# ------------------------------------------------------------------
# Private helper
# ------------------------------------------------------------------


def _validate_yaml_range(
    result: ValidationAccumulator,
    value: int | float,
    char: Any,  # noqa: ANN401  # BaseCharacteristic back-reference
) -> None:
    """Add YAML-derived range validation errors to *result* (mutates in-place).

    Only applies when no class-level min/max constraints are set.
    """
    spec: CharacteristicSpec | None = char._spec  # Internal composition
    if char.min_value is not None or char.max_value is not None or not spec or not spec.structure:
        return

    for field in spec.structure:
        yaml_range = field.value_range
        if yaml_range is not None:
            min_val, max_val = yaml_range
            # Use tolerance for floating-point comparison (common in scaled characteristics)
            tolerance = max(abs(max_val - min_val) * 1e-9, 1e-9) if isinstance(value, float) else 0
            if value < min_val - tolerance or value > max_val + tolerance:
                yaml_source = f"{spec.name}" if spec.name else "YAML specification"
                error_msg = (
                    f"Value {value} is outside allowed range [{min_val}, {max_val}] "
                    f"(source: Bluetooth SIG {yaml_source})"
                )
                if char.unit:
                    error_msg += f" [unit: {char.unit}]"
                result.add_error(error_msg)
            break  # Use first field with range found
