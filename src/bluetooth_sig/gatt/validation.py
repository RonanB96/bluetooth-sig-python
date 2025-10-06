"""Enhanced validation utilities for strict type checking and data validation.

This module provides additional validation capabilities beyond the basic
utils, focusing on strict type safety and comprehensive data integrity
checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from .characteristics.utils.ieee11073_parser import IEEE11073Parser
from .constants import (
    ABSOLUTE_ZERO_CELSIUS,
    MAX_CONCENTRATION_PPM,
    MAX_POWER_WATTS,
    MAX_TEMPERATURE_CELSIUS,
    PERCENTAGE_MAX,
)
from .exceptions import (
    DataValidationError,
    TypeMismatchError,
    ValueRangeError,
)

T = TypeVar("T")


@dataclass
class ValidationRule:
    """Represents a validation rule with optional custom validator."""

    field_name: str
    expected_type: type | tuple[type, ...]  # Allow tuple of types for isinstance
    min_value: int | float | None = None
    max_value: int | float | None = None
    custom_validator: Callable[[Any], bool] | None = None
    error_message: str | None = None

    def validate(self, value: Any) -> None:
        """Apply this validation rule to a value."""
        # Type check
        if not isinstance(value, self.expected_type):
            raise TypeMismatchError(self.field_name, value, self.expected_type)

        # Range check
        if self.min_value is not None or self.max_value is not None:
            min_val = self.min_value if self.min_value is not None else float("-inf")
            max_val = self.max_value if self.max_value is not None else float("inf")
            if not min_val <= value <= max_val:
                raise ValueRangeError(self.field_name, value, min_val, max_val)

        # Custom validation
        if self.custom_validator and not self.custom_validator(value):
            message = self.error_message or f"Custom validation failed for {self.field_name}"
            raise DataValidationError(self.field_name, value, message)


@dataclass
class StrictValidator:
    """Strict validation engine for complex data structures."""

    rules: dict[str, ValidationRule] = field(default_factory=dict)

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules[rule.field_name] = rule

    def validate_dict(self, data: dict[str, Any]) -> None:
        """Validate a dictionary against all rules."""
        for field_name, value in data.items():
            if field_name in self.rules:
                self.rules[field_name].validate(value)

    def validate_object(self, obj: Any) -> None:
        """Validate an object's attributes against all rules."""
        for field_name, rule in self.rules.items():
            if hasattr(obj, field_name):
                value = getattr(obj, field_name)
                rule.validate(value)


class CommonValidators:
    """Collection of commonly used validation functions."""

    @staticmethod
    def is_positive(value: int | float) -> bool:
        """Check if value is positive."""
        return value > 0

    @staticmethod
    def is_non_negative(value: int | float) -> bool:
        """Check if value is non-negative."""
        return value >= 0

    @staticmethod
    def is_valid_percentage(value: int | float) -> bool:
        """Check if value is a valid percentage (0-100)."""
        return 0 <= value <= PERCENTAGE_MAX

    @staticmethod
    def is_valid_extended_percentage(value: int | float) -> bool:
        """Check if value is a valid extended percentage (0-200)."""
        return 0 <= value <= 200

    @staticmethod
    def is_physical_temperature(value: float) -> bool:
        """Check if temperature is physically reasonable."""
        return ABSOLUTE_ZERO_CELSIUS <= value <= MAX_TEMPERATURE_CELSIUS

    @staticmethod
    def is_valid_concentration(value: float) -> bool:
        """Check if concentration is in valid range."""
        return 0 <= value <= MAX_CONCENTRATION_PPM

    @staticmethod
    def is_valid_power(value: int | float) -> bool:
        """Check if power value is reasonable."""
        return 0 <= value <= MAX_POWER_WATTS

    @staticmethod
    def is_valid_heart_rate(value: int) -> bool:
        """Check if heart rate is in human range."""
        return 30 <= value <= 300  # Reasonable human heart rate range

    @staticmethod
    def is_valid_battery_level(value: int) -> bool:
        """Check if battery level is valid percentage."""
        return 0 <= value <= PERCENTAGE_MAX

    @staticmethod
    def is_ieee11073_special_value(value: int) -> bool:
        """Check if value is a valid IEEE 11073 special value."""
        special_values = {
            IEEE11073Parser.SFLOAT_NAN,
            IEEE11073Parser.SFLOAT_NRES,
            IEEE11073Parser.SFLOAT_POSITIVE_INFINITY,
            IEEE11073Parser.SFLOAT_NEGATIVE_INFINITY,
        }
        return value in special_values


# Pre-configured validators for common use cases
HEART_RATE_VALIDATOR = StrictValidator()
HEART_RATE_VALIDATOR.add_rule(
    ValidationRule(
        field_name="heart_rate",
        expected_type=int,
        min_value=30,
        max_value=300,
        custom_validator=CommonValidators.is_valid_heart_rate,
        error_message="Heart rate must be between 30-300 bpm",
    )
)

BATTERY_VALIDATOR = StrictValidator()
BATTERY_VALIDATOR.add_rule(
    ValidationRule(
        field_name="battery_level",
        expected_type=int,
        min_value=0,
        max_value=PERCENTAGE_MAX,
        custom_validator=CommonValidators.is_valid_battery_level,
        error_message="Battery level must be 0-100%",
    )
)

TEMPERATURE_VALIDATOR = StrictValidator()
TEMPERATURE_VALIDATOR.add_rule(
    ValidationRule(
        field_name="temperature",
        expected_type=float,
        min_value=ABSOLUTE_ZERO_CELSIUS,
        max_value=MAX_TEMPERATURE_CELSIUS,
        custom_validator=CommonValidators.is_physical_temperature,
        error_message="Temperature must be physically reasonable",
    )
)


def create_range_validator(
    field_name: str,
    expected_type: type,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    custom_validator: Callable[[Any], bool] | None = None,
) -> StrictValidator:
    """Factory function to create a validator for a specific range."""
    validator = StrictValidator()
    validator.add_rule(
        ValidationRule(
            field_name=field_name,
            expected_type=expected_type,
            min_value=min_value,
            max_value=max_value,
            custom_validator=custom_validator,
        )
    )
    return validator


def validate_measurement_data(data: dict[str, Any], measurement_type: str) -> dict[str, Any]:
    """Validate measurement data based on type and return validated data."""
    if measurement_type == "heart_rate":
        HEART_RATE_VALIDATOR.validate_dict(data)
    elif measurement_type == "battery":
        BATTERY_VALIDATOR.validate_dict(data)
    elif measurement_type == "temperature":
        TEMPERATURE_VALIDATOR.validate_dict(data)
    else:
        # Generic validation for unknown types
        for key, value in data.items():
            if isinstance(value, (int, float)) and value < 0:
                raise ValueRangeError(key, value, 0, float("inf"))

    return data
