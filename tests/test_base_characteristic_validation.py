"""Tests for BaseCharacteristic validation attributes functionality."""

from dataclasses import dataclass

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic


@dataclass
class ValidationHelperCharacteristic(BaseCharacteristic):
    """Helper characteristic with validation attributes."""

    _characteristic_name: str = "Test Validation"

    # Validation attributes
    expected_length: int = 2
    min_value: int = 0
    max_value: int = 100
    expected_type: type = int

    def __post_init__(self):
        # Set a dummy UUID to avoid resolution issues
        self._char_uuid = "TEST-UUID"

    def decode_value(self, data: bytearray) -> int:
        """Simple decode - just parse as uint16."""
        if len(data) < 2:
            raise ValueError("Need at least 2 bytes")
        return int.from_bytes(data[:2], byteorder="little", signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Simple encode."""
        return bytearray(data.to_bytes(2, byteorder="little", signed=False))


@dataclass
class NoValidationCharacteristic(BaseCharacteristic):
    """Test characteristic without validation attributes."""

    _characteristic_name: str = "No Validation"

    def __post_init__(self):
        self._char_uuid = "NO-VALIDATION-UUID"

    def decode_value(self, data: bytearray) -> int:
        """Simple decode without validation."""
        return 42

    def encode_value(self, data: int) -> bytearray:
        """Simple encode."""
        return bytearray([42])


class TestBaseCharacteristicValidation:
    """Test the new validation functionality in BaseCharacteristic."""

    def test_successful_parse_with_validation(self):
        """Test successful parsing when all validations pass."""
        char = ValidationHelperCharacteristic(uuid="TEST", properties=set())
        data = bytearray([50, 0])  # 50 in little endian, within range 0-100

        result = char.parse_value(data)

        assert result.parse_success is True
        assert result.value == 50
        assert result.error_message is None
        assert result.raw_data == bytes([50, 0])
        assert result.name == "Test Validation"

    def test_length_validation_failure(self):
        """Test parsing failure when length validation fails."""
        char = ValidationHelperCharacteristic(uuid="TEST", properties=set())
        data = bytearray([50])  # Only 1 byte, expected 2

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Expected 2 bytes, got 1" in result.error_message
        assert result.raw_data == bytes([50])

    def test_parse_with_decode_error(self):
        """Test parsing when decode_value raises an exception."""
        char = ValidationHelperCharacteristic(uuid="TEST", properties=set())
        data = bytearray([200, 0])  # 200 is out of range 0-100

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Value 200 exceeds maximum 100" in str(result.error_message)

    def test_range_validation_failure_min(self):
        """Test that minimum value validation failures are handled correctly."""

        @dataclass
        class MinValueCharacteristic(BaseCharacteristic):
            _characteristic_name: str = "Min Value Test"
            min_value: int = 10
            max_value: int = 100

            def __post_init__(self):
                self._char_uuid = "MIN-VALUE-UUID"

            def decode_value(self, data: bytearray) -> int:
                return 5  # Below min_value of 10

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MinValueCharacteristic(uuid="TEST", properties=set())
        data = bytearray([1, 2])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Value 5 below minimum 10" in result.error_message

    def test_type_validation_failure(self):
        """Test that type validation failures are handled correctly."""

        @dataclass
        class TypeValidationCharacteristic(BaseCharacteristic):
            _characteristic_name: str = "Type Test"
            expected_type: type = float

            def __post_init__(self):
                self._char_uuid = "TYPE-UUID"

            def decode_value(
                self, data: bytearray
            ) -> int:  # Returns int but expects float
                return 42

            def encode_value(self, data) -> bytearray:
                return bytearray()

        char = TypeValidationCharacteristic(uuid="TEST", properties=set())
        data = bytearray([1, 2])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Expected float, got int" in result.error_message

    def test_no_validation_attributes(self):
        """Test that characteristics without validation attributes work normally."""
        char = NoValidationCharacteristic(uuid="TEST", properties=set())
        data = bytearray([1, 2, 3, 4, 5])  # Any length should work

        result = char.parse_value(data)

        assert result.parse_success is True
        assert result.value == 42
        assert result.error_message is None

    def test_min_length_validation(self):
        """Test minimum length validation."""

        @dataclass
        class MinLengthCharacteristic(BaseCharacteristic):
            _characteristic_name: str = "Min Length Test"
            min_length: int = 3

            def __post_init__(self):
                self._char_uuid = "MIN-LENGTH-UUID"

            def decode_value(self, data: bytearray) -> int:
                return len(data)

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MinLengthCharacteristic(uuid="TEST", properties=set())

        # Test with too short data
        result = char.parse_value(bytearray([1, 2]))  # 2 bytes < min_length 3
        assert result.parse_success is False
        assert "Minimum 3 bytes required, got 2" in result.error_message

        # Test with sufficient data
        result = char.parse_value(bytearray([1, 2, 3, 4]))  # 4 bytes >= min_length 3
        assert result.parse_success is True
        assert result.value == 4

    def test_max_length_validation(self):
        """Test maximum length validation."""

        @dataclass
        class MaxLengthCharacteristic(BaseCharacteristic):
            _characteristic_name: str = "Max Length Test"
            max_length: int = 3

            def __post_init__(self):
                self._char_uuid = "MAX-LENGTH-UUID"

            def decode_value(self, data: bytearray) -> int:
                return len(data)

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MaxLengthCharacteristic(uuid="TEST", properties=set())

        # Test with too long data
        result = char.parse_value(bytearray([1, 2, 3, 4]))  # 4 bytes > max_length 3
        assert result.parse_success is False
        assert "Maximum 3 bytes allowed, got 4" in result.error_message

        # Test with acceptable data
        result = char.parse_value(bytearray([1, 2]))  # 2 bytes <= max_length 3
        assert result.parse_success is True
        assert result.value == 2

    def test_decode_value_exception_handling(self):
        """Test that exceptions from decode_value are properly handled."""

        @dataclass
        class ExceptionCharacteristic(BaseCharacteristic):
            _characteristic_name: str = "Exception Test"

            def __post_init__(self):
                self._char_uuid = "EXCEPTION-UUID"

            def decode_value(self, data: bytearray) -> int:
                raise ValueError("Custom decode error")

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = ExceptionCharacteristic(uuid="TEST", properties=set())
        data = bytearray([1, 2])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Custom decode error" in result.error_message

    def test_struct_error_handling(self):
        """Test that struct.error exceptions are properly handled."""
        import struct

        @dataclass
        class StructErrorCharacteristic(BaseCharacteristic):
            _characteristic_name: str = "Struct Error Test"

            def __post_init__(self):
                self._char_uuid = "STRUCT-ERROR-UUID"

            def decode_value(self, data: bytearray) -> int:
                # This will raise struct.error due to insufficient data
                return struct.unpack("<I", data)[0]  # Needs 4 bytes for uint32

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = StructErrorCharacteristic(uuid="TEST", properties=set())
        data = bytearray([1, 2])  # Only 2 bytes, but struct expects 4

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert result.error_message is not None  # Should contain struct error message
