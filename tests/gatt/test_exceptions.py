"""Tests for the exceptions module."""

import pytest

from bluetooth_sig.gatt.exceptions import (
    BluetoothSIGError,
    CharacteristicError,
    DataEncodingError,
    DataParsingError,
    DataValidationError,
    EnumValueError,
    IEEE11073Error,
    InsufficientDataError,
    ServiceCharacteristicMismatchError,
    ServiceError,
    TemplateConfigurationError,
    TypeMismatchError,
    UUIDResolutionError,
    ValueRangeError,
    YAMLResolutionError,
)


class TestBluetoothSIGExceptions:
    """Test exception hierarchy and functionality."""

    def test_base_exception_inheritance(self) -> None:
        """Test that all exceptions inherit from BluetoothSIGError."""
        # Test inheritance chain
        assert issubclass(CharacteristicError, BluetoothSIGError)
        assert issubclass(ServiceError, BluetoothSIGError)
        assert issubclass(UUIDResolutionError, BluetoothSIGError)
        assert issubclass(DataParsingError, CharacteristicError)
        assert issubclass(DataValidationError, CharacteristicError)

    def test_uuid_resolution_error(self) -> None:
        """Test UUIDResolutionError functionality."""
        # Basic error
        error = UUIDResolutionError("SomeCharacteristic")
        assert error.name == "SomeCharacteristic"
        assert error.attempted_names == []
        assert "No UUID found for: SomeCharacteristic" in str(error)

        # Error with attempted names
        attempted = ["Some", "SomeCharacteristic", "org.bluetooth.characteristic.some"]
        error_with_attempts = UUIDResolutionError("SomeCharacteristic", attempted)
        assert error_with_attempts.attempted_names == attempted
        assert "Tried:" in str(error_with_attempts)

    def test_data_parsing_error(self) -> None:
        """Test DataParsingError functionality."""
        test_data = b"\x01\x02\x03"
        error = DataParsingError("TestCharacteristic", test_data, "Invalid format")

        assert error.characteristic == "TestCharacteristic"
        assert error.data == test_data
        assert error.reason == "Invalid format"
        assert "Failed to parse TestCharacteristic data [01 02 03]" in str(error)
        assert "Invalid format" in str(error)

    def test_data_encoding_error(self) -> None:
        """Test DataEncodingError functionality."""
        test_value = 42
        error = DataEncodingError("TestCharacteristic", test_value, "Invalid range")

        assert error.characteristic == "TestCharacteristic"
        assert error.value == test_value
        assert error.reason == "Invalid range"
        assert "Failed to encode TestCharacteristic value 42" in str(error)

    def test_data_validation_error(self) -> None:
        """Test DataValidationError functionality."""
        error = DataValidationError("temperature", -300, "valid temperature range")

        assert error.field == "temperature"
        assert error.value == -300
        assert error.expected == "valid temperature range"
        assert "Invalid temperature: -300 (expected valid temperature range)" in str(error)

    def test_insufficient_data_error(self) -> None:
        """Test InsufficientDataError functionality."""
        test_data = b"\x01\x02"
        error = InsufficientDataError("TestCharacteristic", test_data, 4)

        assert error.characteristic == "TestCharacteristic"
        assert error.data == test_data
        assert error.required == 4
        assert error.actual == 2
        assert "need 4 bytes, got 2" in str(error)

    def test_value_range_error(self) -> None:
        """Test ValueRangeError functionality."""
        error = ValueRangeError("temperature", 150, -40, 85)

        assert error.field == "temperature"
        assert error.value == 150
        assert error.min_val == -40
        assert error.max_val == 85
        assert "Invalid temperature: 150 (expected range [-40, 85])" in str(error)

    def test_type_mismatch_error_single_type(self) -> None:
        """Test TypeMismatchError with single expected type."""
        error = TypeMismatchError("value", "string", int)

        assert error.field == "value"
        assert error.value == "string"
        assert error.expected_type is int
        assert error.actual_type is str
        assert "expected type int, got str" in str(error)

    def test_type_mismatch_error_tuple_types(self) -> None:
        """Test TypeMismatchError with tuple of expected types."""
        error = TypeMismatchError("value", "string", (int, float))

        assert error.field == "value"
        assert error.value == "string"
        assert error.expected_type == (int, float)
        assert error.actual_type is str
        assert "expected type int or float, got str" in str(error)

    def test_enum_value_error(self) -> None:
        """Test EnumValueError functionality."""
        from enum import Enum  # pylint: disable=import-outside-toplevel

        class TestEnum(Enum):  # pylint: disable=too-few-public-methods
            """Test enumeration for validation testing."""

            A = 1
            B = 2

        valid_values = [1, 2]
        error = EnumValueError("mode", 3, TestEnum, valid_values)

        assert error.field == "mode"
        assert error.value == 3
        assert error.enum_class == TestEnum
        assert error.valid_values == valid_values
        assert "TestEnum value from [1, 2]" in str(error)

    def test_ieee11073_error(self) -> None:
        """Test IEEE11073Error functionality."""
        test_data = b"\xff\xff"
        error = IEEE11073Error(test_data, "SFLOAT", "Invalid mantissa")

        assert error.format_type == "SFLOAT"
        assert error.data == test_data
        assert error.reason == "Invalid mantissa"
        assert "Failed to parse IEEE 11073 SFLOAT data" in str(error)

    def test_yaml_resolution_error(self) -> None:
        """Test YAMLResolutionError functionality."""
        error = YAMLResolutionError("SomeCharacteristic", "characteristic")

        assert error.name == "SomeCharacteristic"
        assert error.yaml_type == "characteristic"
        assert "Failed to resolve characteristic specification for: SomeCharacteristic" in str(error)

    def test_service_characteristic_mismatch_error(self) -> None:
        """Test ServiceCharacteristicMismatchError functionality."""
        missing = ["BatteryLevel", "DeviceInformation"]
        error = ServiceCharacteristicMismatchError("BatteryService", missing)

        assert error.service == "BatteryService"
        assert error.missing_characteristics == missing
        assert "Service BatteryService missing required characteristics" in str(error)
        assert "BatteryLevel, DeviceInformation" in str(error)

    def test_template_configuration_error(self) -> None:
        """Test TemplateConfigurationError functionality."""
        error = TemplateConfigurationError("GenericTemplate", "Missing required field")

        assert error.template == "GenericTemplate"
        assert error.configuration_issue == "Missing required field"
        assert "Template GenericTemplate configuration error" in str(error)

    def test_exception_inheritance_with_isinstance(self) -> None:
        """Test isinstance checks work correctly."""
        # Create specific exceptions
        data_error = DataParsingError("test", b"\x01", "reason")
        validation_error = DataValidationError("field", "value", "expected")

        # Test inheritance checks
        assert isinstance(data_error, DataParsingError)
        assert isinstance(data_error, CharacteristicError)
        assert isinstance(data_error, BluetoothSIGError)
        assert isinstance(data_error, Exception)

        assert isinstance(validation_error, DataValidationError)
        assert isinstance(validation_error, CharacteristicError)
        assert isinstance(validation_error, BluetoothSIGError)

    def test_exception_can_be_raised_and_caught(self) -> None:
        """Test exceptions can be properly raised and caught."""
        with pytest.raises(UUIDResolutionError) as exc_info:
            raise UUIDResolutionError("TestCharacteristic", ["Test", "TestChar"])

        assert exc_info.value.name == "TestCharacteristic"
        assert "TestCharacteristic" in str(exc_info.value)

        with pytest.raises(BluetoothSIGError):
            raise DataParsingError("test", b"\x01", "error")
