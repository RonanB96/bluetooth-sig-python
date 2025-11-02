"""Test cases for data validation utilities."""

from __future__ import annotations

from enum import IntEnum

import pytest

from bluetooth_sig.gatt.characteristics.utils.data_validator import DataValidator
from bluetooth_sig.gatt.exceptions import DataValidationError, EnumValueError, ValueRangeError


class SampleEnum(IntEnum):
    """Sample enum for testing enum validation."""

    FIRST = 1
    SECOND = 2
    THIRD = 3


class TestDataLengthValidation:
    """Test data length validation."""

    def test_validate_data_length_valid(self) -> None:
        """Test data length validation with valid lengths."""
        data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])

        # Minimum length only
        DataValidator.validate_data_length(data, 3)  # Should not raise
        DataValidator.validate_data_length(data, 5)  # Should not raise

        # Minimum and maximum length
        DataValidator.validate_data_length(data, 3, 7)  # Should not raise
        DataValidator.validate_data_length(data, 5, 5)  # Should not raise

    def test_validate_data_length_too_short(self) -> None:
        """Test data length validation with insufficient data."""
        data = bytearray([0x01, 0x02])

        with pytest.raises(DataValidationError):
            DataValidator.validate_data_length(data, 5)

        with pytest.raises(DataValidationError):
            DataValidator.validate_data_length(data, 3, 10)

    def test_validate_data_length_too_long(self) -> None:
        """Test data length validation with excessive data."""
        data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])

        with pytest.raises(DataValidationError):
            DataValidator.validate_data_length(data, 1, 5)

    def test_validate_data_length_empty_data(self) -> None:
        """Test data length validation with empty data."""
        data = bytearray()

        # Empty data is valid if minimum is 0
        DataValidator.validate_data_length(data, 0)  # Should not raise
        DataValidator.validate_data_length(data, 0, 5)  # Should not raise

        # Empty data is invalid if minimum > 0
        with pytest.raises(DataValidationError):
            DataValidator.validate_data_length(data, 1)


class TestRangeValidation:
    """Test numeric range validation."""

    def test_validate_range_integers(self) -> None:
        """Test range validation with integers."""
        # Valid values
        DataValidator.validate_range(5, 0, 10)  # Should not raise
        DataValidator.validate_range(0, 0, 10)  # Boundary - min
        DataValidator.validate_range(10, 0, 10)  # Boundary - max

        # Invalid values
        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(-1, 0, 10)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(11, 0, 10)

    def test_validate_range_floats(self) -> None:
        """Test range validation with floats."""
        # Valid values
        DataValidator.validate_range(5.5, 0.0, 10.0)  # Should not raise
        DataValidator.validate_range(0.0, 0.0, 10.0)  # Boundary - min
        DataValidator.validate_range(10.0, 0.0, 10.0)  # Boundary - max

        # Invalid values
        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(-0.1, 0.0, 10.0)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(10.1, 0.0, 10.0)

    def test_validate_range_negative_ranges(self) -> None:
        """Test range validation with negative ranges."""
        # Valid values in negative range
        DataValidator.validate_range(-5, -10, 0)  # Should not raise
        DataValidator.validate_range(-10, -10, 0)  # Boundary - min
        DataValidator.validate_range(0, -10, 0)  # Boundary - max

        # Invalid values
        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(-11, -10, 0)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(1, -10, 0)


class TestEnumValidation:
    """Test enum value validation."""

    def test_validate_enum_value_valid(self) -> None:
        """Test enum validation with valid values."""
        DataValidator.validate_enum_value(1, SampleEnum)  # Should not raise
        DataValidator.validate_enum_value(2, SampleEnum)  # Should not raise
        DataValidator.validate_enum_value(3, SampleEnum)  # Should not raise

    def test_validate_enum_value_invalid(self) -> None:
        """Test enum validation with invalid values."""
        with pytest.raises(EnumValueError):
            DataValidator.validate_enum_value(0, SampleEnum)
        with pytest.raises(EnumValueError):
            DataValidator.validate_enum_value(4, SampleEnum)
        with pytest.raises(EnumValueError):
            DataValidator.validate_enum_value(-1, SampleEnum)

    def test_validate_enum_value_error_details(self) -> None:
        """Test enum validation error contains proper details."""
        try:
            DataValidator.validate_enum_value(99, SampleEnum)
            pytest.fail("Expected EnumValueError")
        except EnumValueError as e:
            assert "SampleEnum" in str(e)
            assert "99" in str(e)


class TestConcentrationValidation:
    """Test concentration range validation."""

    def test_validate_concentration_range_valid(self) -> None:
        """Test concentration validation with valid values."""
        DataValidator.validate_concentration_range(0.0)  # Should not raise
        DataValidator.validate_concentration_range(500.0)  # Should not raise
        DataValidator.validate_concentration_range(1000.0)  # Default max

        # Custom max
        DataValidator.validate_concentration_range(2000.0, max_ppm=2500.0)  # Should not raise

    def test_validate_concentration_range_invalid(self) -> None:
        """Test concentration validation with invalid values."""
        # Below minimum
        with pytest.raises(ValueRangeError):
            DataValidator.validate_concentration_range(-1.0)

        # Above default maximum
        with pytest.raises(ValueRangeError):
            DataValidator.validate_concentration_range(100001.0)  # Much higher than reasonable max

        # Above custom maximum
        with pytest.raises(ValueRangeError):
            DataValidator.validate_concentration_range(2501.0, max_ppm=2500.0)

    def test_validate_concentration_range_edge_cases(self) -> None:
        """Test concentration validation edge cases."""
        # Exactly at boundaries
        DataValidator.validate_concentration_range(0.0)  # Min boundary
        DataValidator.validate_concentration_range(1000.0)  # Max boundary

        # Very small positive value
        DataValidator.validate_concentration_range(0.001)  # Should not raise


class TestTemperatureValidation:
    """Test temperature range validation."""

    def test_validate_temperature_range_valid(self) -> None:
        """Test temperature validation with valid values."""
        DataValidator.validate_temperature_range(20.0)  # Room temperature
        DataValidator.validate_temperature_range(37.0)  # Body temperature
        DataValidator.validate_temperature_range(-273.15)  # Absolute zero (default min)
        DataValidator.validate_temperature_range(100.0)  # Boiling point

        # Custom ranges
        DataValidator.validate_temperature_range(50.0, min_celsius=0.0, max_celsius=100.0)

    def test_validate_temperature_range_invalid(self) -> None:
        """Test temperature validation with invalid values."""
        # Below absolute zero (default)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_temperature_range(-274.0)

        # Above maximum (assuming reasonable medical/environmental max)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_temperature_range(10000.0)  # Much higher than reasonable max

        # Custom range violations
        with pytest.raises(ValueRangeError):
            DataValidator.validate_temperature_range(-1.0, min_celsius=0.0, max_celsius=100.0)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_temperature_range(101.0, min_celsius=0.0, max_celsius=100.0)

    def test_validate_temperature_range_edge_cases(self) -> None:
        """Test temperature validation edge cases."""
        # Exactly at absolute zero
        DataValidator.validate_temperature_range(-273.15)  # Should not raise

        # Fahrenheit equivalent temperatures (should be converted to Celsius before validation)
        # 32°F = 0°C, 212°F = 100°C, etc.


class TestPercentageValidation:
    """Test percentage validation."""

    def test_validate_percentage_normal(self) -> None:
        """Test percentage validation for normal 0-100% range."""
        DataValidator.validate_percentage(0)  # Should not raise
        DataValidator.validate_percentage(50)  # Should not raise
        DataValidator.validate_percentage(100)  # Should not raise
        DataValidator.validate_percentage(0.0)  # Should not raise
        DataValidator.validate_percentage(50.5)  # Should not raise
        DataValidator.validate_percentage(100.0)  # Should not raise

    def test_validate_percentage_extended(self) -> None:
        """Test percentage validation for extended 0-200% range."""
        DataValidator.validate_percentage(150, allow_over_100=True)  # Should not raise
        DataValidator.validate_percentage(200, allow_over_100=True)  # Should not raise
        DataValidator.validate_percentage(200.0, allow_over_100=True)  # Should not raise

    def test_validate_percentage_invalid_normal(self) -> None:
        """Test percentage validation with invalid values (normal range)."""
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(-1)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(101)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(-0.1)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(100.1)

    def test_validate_percentage_invalid_extended(self) -> None:
        """Test percentage validation with invalid values (extended range)."""
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(-1, allow_over_100=True)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(201, allow_over_100=True)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(-0.1, allow_over_100=True)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(200.1, allow_over_100=True)

    def test_validate_percentage_edge_cases(self) -> None:
        """Test percentage validation edge cases."""
        # Exactly at boundaries
        DataValidator.validate_percentage(0)  # Min normal
        DataValidator.validate_percentage(100)  # Max normal
        DataValidator.validate_percentage(200, allow_over_100=True)  # Max extended

        # Fractional percentages
        DataValidator.validate_percentage(99.99)  # Should not raise
        DataValidator.validate_percentage(199.99, allow_over_100=True)  # Should not raise


class TestPowerValidation:
    """Test power range validation."""

    def test_validate_power_range_valid(self) -> None:
        """Test power validation with valid values."""
        DataValidator.validate_power_range(0)  # Minimum
        DataValidator.validate_power_range(100)  # Typical value
        DataValidator.validate_power_range(1000)  # High value
        DataValidator.validate_power_range(0.0)  # Float minimum
        DataValidator.validate_power_range(500.5)  # Float value

        # Custom maximum
        DataValidator.validate_power_range(2000, max_watts=2500)

    def test_validate_power_range_invalid(self) -> None:
        """Test power validation with invalid values."""
        # Negative power
        with pytest.raises(ValueRangeError):
            DataValidator.validate_power_range(-1)
        with pytest.raises(ValueRangeError):
            DataValidator.validate_power_range(-0.1)

        # Exceeding maximum (assuming default max exists)
        # Note: MAX_POWER_WATTS constant determines actual limit

        # Custom maximum violations
        with pytest.raises(ValueRangeError):
            DataValidator.validate_power_range(2501, max_watts=2500)

    def test_validate_power_range_edge_cases(self) -> None:
        """Test power validation edge cases."""
        # Exactly at minimum
        DataValidator.validate_power_range(0)  # Should not raise
        DataValidator.validate_power_range(0.0)  # Should not raise

        # Very small positive values
        DataValidator.validate_power_range(0.001)  # Should not raise


class TestValidationIntegration:
    """Test validation utilities working together."""

    def test_multiple_validations_success(self) -> None:
        """Test multiple validations all passing."""
        data = bytearray([0x01, 0x02, 0x03, 0x04])

        # All should pass
        DataValidator.validate_data_length(data, 3, 5)
        DataValidator.validate_range(4, 0, 10)  # len(data)
        DataValidator.validate_enum_value(2, SampleEnum)  # data[1]
        DataValidator.validate_percentage(50)
        DataValidator.validate_concentration_range(100.0)
        DataValidator.validate_temperature_range(25.0)
        DataValidator.validate_power_range(150)

    def test_validation_error_propagation(self) -> None:
        """Test that validation errors are properly propagated."""
        # Each validation should raise appropriate exception type
        with pytest.raises(DataValidationError):
            DataValidator.validate_data_length(bytearray(), 1)

        with pytest.raises(ValueRangeError):
            DataValidator.validate_range(11, 0, 10)

        with pytest.raises(EnumValueError):
            DataValidator.validate_enum_value(99, SampleEnum)

        with pytest.raises(ValueRangeError):
            DataValidator.validate_percentage(101)

        with pytest.raises(ValueRangeError):
            DataValidator.validate_concentration_range(-1.0)

        with pytest.raises(ValueRangeError):
            DataValidator.validate_temperature_range(-300.0)

        with pytest.raises(ValueRangeError):
            DataValidator.validate_power_range(-1)

    def test_boundary_value_consistency(self) -> None:
        """Test that boundary values are consistently handled."""
        # All minimum values should be valid
        DataValidator.validate_range(0, 0, 10)
        DataValidator.validate_percentage(0)
        DataValidator.validate_concentration_range(0.0)
        DataValidator.validate_power_range(0)

        # All maximum values should be valid (within respective ranges)
        DataValidator.validate_range(10, 0, 10)
        DataValidator.validate_percentage(100)
        DataValidator.validate_percentage(200, allow_over_100=True)
