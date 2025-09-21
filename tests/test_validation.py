"""Tests for the validation module."""

import pytest

from bluetooth_sig.gatt.exceptions import (
    DataValidationError,
    TypeMismatchError,
    ValueRangeError,
)
from bluetooth_sig.gatt.validation import (
    CommonValidators,
    StrictValidator,
    ValidationRule,
)


class TestValidationRule:
    """Test ValidationRule class functionality."""

    def test_basic_type_validation_success(self):
        """Test successful type validation."""
        rule = ValidationRule("temperature", float)

        # Should not raise for correct type
        rule.validate(25.5)
        rule.validate(0.0)
        rule.validate(-10.5)

    def test_basic_type_validation_failure(self):
        """Test type validation failure."""
        rule = ValidationRule("temperature", float)

        with pytest.raises(TypeMismatchError) as exc_info:
            rule.validate("not a float")

        assert exc_info.value.field == "temperature"
        assert exc_info.value.value == "not a float"
        assert exc_info.value.expected_type is float

    def test_tuple_type_validation_success(self):
        """Test validation with tuple of allowed types."""
        rule = ValidationRule("value", (int, float))

        # Should not raise for either type
        rule.validate(42)
        rule.validate(42.5)

    def test_tuple_type_validation_failure(self):
        """Test validation failure with tuple of types."""
        rule = ValidationRule("value", (int, float))

        with pytest.raises(TypeMismatchError) as exc_info:
            rule.validate("string")

        assert "int or float" in str(exc_info.value)

    def test_range_validation_success(self):
        """Test successful range validation."""
        rule = ValidationRule("percentage", float, min_value=0.0, max_value=100.0)

        # Valid values
        rule.validate(0.0)
        rule.validate(50.0)
        rule.validate(100.0)

    def test_range_validation_failure_min(self):
        """Test range validation failure (below minimum)."""
        rule = ValidationRule("percentage", float, min_value=0.0, max_value=100.0)

        with pytest.raises(ValueRangeError) as exc_info:
            rule.validate(-10.0)

        assert exc_info.value.field == "percentage"
        assert exc_info.value.value == -10.0
        assert exc_info.value.min_val == 0.0
        assert exc_info.value.max_val == 100.0

    def test_range_validation_failure_max(self):
        """Test range validation failure (above maximum)."""
        rule = ValidationRule("percentage", float, min_value=0.0, max_value=100.0)

        with pytest.raises(ValueRangeError) as exc_info:
            rule.validate(150.0)

        assert exc_info.value.value == 150.0

    def test_custom_validator_success(self):
        """Test successful custom validation."""

        def is_even(value: int) -> bool:
            return value % 2 == 0

        rule = ValidationRule("even_number", int, custom_validator=is_even)

        # Should not raise for even numbers
        rule.validate(2)
        rule.validate(42)
        rule.validate(0)

    def test_custom_validator_failure(self):
        """Test custom validation failure."""

        def is_even(value: int) -> bool:
            return value % 2 == 0

        rule = ValidationRule("even_number", int, custom_validator=is_even)

        with pytest.raises(DataValidationError) as exc_info:
            rule.validate(3)

        assert "Custom validation failed" in str(exc_info.value)

    def test_custom_error_message(self):
        """Test custom error message."""

        def is_positive(value: float) -> bool:
            return value > 0

        rule = ValidationRule(
            "positive_value",
            float,
            custom_validator=is_positive,
            error_message="Value must be positive",
        )

        with pytest.raises(DataValidationError) as exc_info:
            rule.validate(-5.0)

        assert "Value must be positive" in str(exc_info.value)

    def test_min_only_validation(self):
        """Test validation with only minimum value."""
        rule = ValidationRule("temperature", float, min_value=-273.15)

        rule.validate(-273.15)  # Should pass
        rule.validate(0.0)  # Should pass
        rule.validate(100.0)  # Should pass

        with pytest.raises(ValueRangeError):
            rule.validate(-300.0)  # Should fail

    def test_max_only_validation(self):
        """Test validation with only maximum value."""
        rule = ValidationRule("temperature", float, max_value=1000.0)

        rule.validate(-100.0)  # Should pass
        rule.validate(0.0)  # Should pass
        rule.validate(1000.0)  # Should pass

        with pytest.raises(ValueRangeError):
            rule.validate(1500.0)  # Should fail


class TestCommonValidators:
    """Test CommonValidators utility functions."""

    def test_is_positive(self):
        """Test positive value validation."""
        assert CommonValidators.is_positive(1.0)
        assert CommonValidators.is_positive(0.001)
        assert not CommonValidators.is_positive(0.0)
        assert not CommonValidators.is_positive(-1.0)

    def test_is_non_negative(self):
        """Test non-negative value validation."""
        assert CommonValidators.is_non_negative(1.0)
        assert CommonValidators.is_non_negative(0.0)
        assert not CommonValidators.is_non_negative(-0.001)

    def test_is_valid_percentage(self):
        """Test percentage validation."""
        assert CommonValidators.is_valid_percentage(0.0)
        assert CommonValidators.is_valid_percentage(50.0)
        assert CommonValidators.is_valid_percentage(100.0)
        assert not CommonValidators.is_valid_percentage(-10.0)
        assert not CommonValidators.is_valid_percentage(150.0)

    def test_is_valid_extended_percentage(self):
        """Test extended percentage validation."""
        assert CommonValidators.is_valid_extended_percentage(0.0)
        assert CommonValidators.is_valid_extended_percentage(100.0)
        assert CommonValidators.is_valid_extended_percentage(200.0)
        assert not CommonValidators.is_valid_extended_percentage(-10.0)
        assert not CommonValidators.is_valid_extended_percentage(250.0)

    def test_is_physical_temperature(self):
        """Test physical temperature validation."""
        assert CommonValidators.is_physical_temperature(-273.15)  # Absolute zero
        assert CommonValidators.is_physical_temperature(0.0)
        assert CommonValidators.is_physical_temperature(100.0)
        assert CommonValidators.is_physical_temperature(1000.0)
        assert not CommonValidators.is_physical_temperature(-300.0)
        assert not CommonValidators.is_physical_temperature(1500.0)

    def test_is_valid_concentration(self):
        """Test concentration validation."""
        assert CommonValidators.is_valid_concentration(0.0)
        assert CommonValidators.is_valid_concentration(1000.0)
        assert CommonValidators.is_valid_concentration(65535.0)
        assert not CommonValidators.is_valid_concentration(-10.0)
        assert not CommonValidators.is_valid_concentration(100000.0)

    def test_is_valid_power(self):
        """Test power validation."""
        assert CommonValidators.is_valid_power(0.0)
        assert CommonValidators.is_valid_power(1000.0)
        assert CommonValidators.is_valid_power(65535.0)
        assert not CommonValidators.is_valid_power(-10.0)
        assert not CommonValidators.is_valid_power(100000.0)


class TestStrictValidator:
    """Test StrictValidator class functionality."""

    def test_add_rule(self):
        """Test adding validation rules."""
        validator = StrictValidator()
        rule = ValidationRule("temperature", float, min_value=-40.0, max_value=85.0)

        validator.add_rule(rule)
        assert "temperature" in validator.rules
        assert validator.rules["temperature"] == rule

    def test_validate_dict_success(self):
        """Test successful dictionary validation."""
        validator = StrictValidator()
        validator.add_rule(
            ValidationRule("temperature", float, min_value=-40.0, max_value=85.0)
        )
        validator.add_rule(
            ValidationRule("humidity", float, min_value=0.0, max_value=100.0)
        )

        data = {"temperature": 25.5, "humidity": 65.0, "other_field": "ignored"}

        # Should not raise
        validator.validate_dict(data)

    def test_validate_dict_failure(self):
        """Test dictionary validation failure."""
        validator = StrictValidator()
        validator.add_rule(
            ValidationRule("temperature", float, min_value=-40.0, max_value=85.0)
        )

        data = {"temperature": 150.0}  # Out of range

        with pytest.raises(ValueRangeError):
            validator.validate_dict(data)

    def test_validate_object_success(self):
        """Test successful object validation."""

        class SensorReading:  # pylint: disable=too-few-public-methods
            """Test sensor reading class."""

            temperature: float
            humidity: float

            def __init__(self, temperature: float, humidity: float) -> None:
                self.temperature = temperature
                self.humidity = humidity

        validator = StrictValidator()
        validator.add_rule(
            ValidationRule("temperature", float, min_value=-40.0, max_value=85.0)
        )
        validator.add_rule(
            ValidationRule("humidity", float, min_value=0.0, max_value=100.0)
        )

        reading = SensorReading(25.5, 65.0)

        # Should not raise
        validator.validate_object(reading)

    def test_validate_object_failure(self):
        """Test object validation failure."""

        class SensorReading:  # pylint: disable=too-few-public-methods
            """Test sensor reading class."""

            temperature: float

            def __init__(self, temperature: float) -> None:
                self.temperature = temperature

        validator = StrictValidator()
        validator.add_rule(
            ValidationRule("temperature", float, min_value=-40.0, max_value=85.0)
        )

        reading = SensorReading(-50.0)  # Out of range

        with pytest.raises(ValueRangeError):
            validator.validate_object(reading)

    def test_validate_object_missing_attribute(self):
        """Test validation skips missing attributes."""

        class PartialReading:  # pylint: disable=too-few-public-methods
            """Test partial reading class."""

            temperature: float

            # humidity intentionally omitted to simulate missing attribute

            def __init__(self, temperature: float) -> None:
                self.temperature = temperature

        validator = StrictValidator()
        validator.add_rule(
            ValidationRule("temperature", float, min_value=-40.0, max_value=85.0)
        )
        validator.add_rule(
            ValidationRule("humidity", float, min_value=0.0, max_value=100.0)
        )

        reading = PartialReading(25.5)

        # Should not raise - missing attributes are ignored
        validator.validate_object(reading)


class TestValidationIntegration:
    """Test validation integration scenarios."""

    def test_combined_validation_rules(self):
        """Test combining multiple validation aspects."""

        # Temperature with type, range, and custom validation
        def not_exactly_zero(value: float) -> bool:
            return value != 0.0

        rule = ValidationRule(
            "non_zero_temperature",
            float,
            min_value=-273.15,
            max_value=1000.0,
            custom_validator=not_exactly_zero,
            error_message="Temperature cannot be exactly zero",
        )

        # Valid values
        rule.validate(25.5)
        rule.validate(-10.0)
        rule.validate(100.0)

        # Invalid type
        with pytest.raises(TypeMismatchError):
            rule.validate("25.5")

        # Invalid range
        with pytest.raises(ValueRangeError):
            rule.validate(-300.0)

        # Invalid custom validation
        with pytest.raises(DataValidationError) as exc_info:
            rule.validate(0.0)

        assert "Temperature cannot be exactly zero" in str(exc_info.value)

    def test_realistic_sensor_validation(self):
        """Test realistic sensor data validation scenario."""
        # Simulate validating sensor reading
        temperature_rule = ValidationRule(
            "temperature", (int, float), min_value=-40.0, max_value=85.0
        )
        humidity_rule = ValidationRule(
            "humidity", (int, float), min_value=0.0, max_value=100.0
        )

        # Valid sensor readings
        temperature_rule.validate(23.5)
        humidity_rule.validate(65.2)

        # Realistic invalid readings
        with pytest.raises(ValueRangeError):
            temperature_rule.validate(-50.0)  # Sensor malfunction

        with pytest.raises(ValueRangeError):
            humidity_rule.validate(120.0)  # Impossible humidity

    def test_validation_with_common_validators(self):
        """Test integration with CommonValidators."""
        # Create rule using CommonValidators
        rule = ValidationRule(
            "percentage",
            (int, float),
            custom_validator=CommonValidators.is_valid_percentage,
            error_message="Invalid percentage value",
        )

        # Valid percentages
        rule.validate(0)
        rule.validate(50.5)
        rule.validate(100)

        # Invalid percentage
        with pytest.raises(DataValidationError) as exc_info:
            rule.validate(150)

        assert "Invalid percentage value" in str(exc_info.value)

    def test_strict_validator_with_multiple_rules(self):
        """Test StrictValidator with multiple complex rules."""
        validator = StrictValidator()

        # Add multiple rules
        validator.add_rule(
            ValidationRule(
                "temperature",
                float,
                min_value=-40.0,
                max_value=85.0,
                custom_validator=CommonValidators.is_physical_temperature,
            )
        )
        validator.add_rule(
            ValidationRule(
                "humidity",
                (int, float),
                custom_validator=CommonValidators.is_valid_percentage,
            )
        )
        validator.add_rule(
            ValidationRule(
                "power", (int, float), custom_validator=CommonValidators.is_valid_power
            )
        )

        # Valid data
        valid_data = {
            "temperature": 25.5,
            "humidity": 65,
            "power": 100.0,
            "unvalidated_field": "ignored",
        }
        validator.validate_dict(valid_data)

        # Invalid data
        invalid_data = {"temperature": -300.0}  # Below absolute zero
        with pytest.raises(ValueRangeError):
            validator.validate_dict(invalid_data)
