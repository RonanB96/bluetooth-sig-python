"""Data validation and integrity checking utilities."""

from __future__ import annotations

from enum import IntEnum

from ...constants import (
    ABSOLUTE_ZERO_CELSIUS,
    EXTENDED_PERCENTAGE_MAX,
    MAX_CONCENTRATION_PPM,
    MAX_POWER_WATTS,
    MAX_TEMPERATURE_CELSIUS,
    PERCENTAGE_MAX,
    PERCENTAGE_MIN,
)
from ...exceptions import DataValidationError, EnumValueError, ValueRangeError


class DataValidator:
    """Utility class for data validation and integrity checking."""

    @staticmethod
    def validate_data_length(
        data: bytearray, expected_min: int, expected_max: int | None = None
    ) -> None:
        """Validate data length against expected range."""
        length = len(data)
        if length < expected_min:
            raise DataValidationError("data", data, f"at least {expected_min} bytes")
        if expected_max is not None and length > expected_max:
            raise DataValidationError(
                "data_length", length, f"at most {expected_max} bytes"
            )

    @staticmethod
    def validate_range(
        value: int | float, min_val: int | float, max_val: int | float
    ) -> None:
        """Validate that a value is within the specified range."""
        if not min_val <= value <= max_val:
            raise ValueRangeError("value", value, min_val, max_val)

    @staticmethod
    def validate_enum_value(value: int, enum_class: type[IntEnum]) -> None:
        """Validate that a value is a valid member of an IntEnum."""
        try:
            enum_class(value)
        except ValueError as e:
            valid_values = [member.value for member in enum_class]
            raise EnumValueError(
                enum_class.__name__, value, enum_class, valid_values
            ) from e

    @staticmethod
    def validate_concentration_range(
        value: float, max_ppm: float = MAX_CONCENTRATION_PPM
    ) -> None:
        """Validate concentration value is in acceptable range."""
        if value < PERCENTAGE_MIN:
            raise ValueRangeError("concentration", value, 0, max_ppm)
        if value > max_ppm:
            raise ValueRangeError("concentration", value, 0, max_ppm)

    @staticmethod
    def validate_temperature_range(
        value: float,
        min_celsius: float = ABSOLUTE_ZERO_CELSIUS,
        max_celsius: float = MAX_TEMPERATURE_CELSIUS,
    ) -> None:
        """Validate temperature is in physically reasonable range."""
        if value < min_celsius:
            raise ValueRangeError("temperature", value, min_celsius, max_celsius)
        if value > max_celsius:
            raise ValueRangeError("temperature", value, min_celsius, max_celsius)

    @staticmethod
    def validate_percentage(value: int | float, allow_over_100: bool = False) -> None:
        """Validate percentage value (0-100% or 0-200% for some characteristics)."""
        max_value = EXTENDED_PERCENTAGE_MAX if allow_over_100 else PERCENTAGE_MAX
        if value < PERCENTAGE_MIN or value > max_value:
            raise ValueRangeError("percentage", value, 0, max_value)

    @staticmethod
    def validate_power_range(
        value: int | float, max_watts: float = MAX_POWER_WATTS
    ) -> None:
        """Validate power measurement range."""
        if value < 0 or value > max_watts:
            raise ValueRangeError("power", value, 0, max_watts)
