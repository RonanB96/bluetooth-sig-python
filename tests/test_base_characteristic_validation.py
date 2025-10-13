"""Tests for BaseCharacteristic validation attributes functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics.base import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class ValidationHelperCharacteristic(CustomBaseCharacteristic):
    """Helper characteristic with validation attributes."""

    # Validation attributes
    expected_length: int | None = 2
    min_value: int | float | None = 0
    max_value: int | float | None = 100
    expected_type: type | None = int

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789012"),
        name="Test Validation",
        unit="",
        value_type=ValueType.INT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Simple decode - just parse as uint16."""
        if len(data) < 2:
            raise ValueError("Need at least 2 bytes")
        return int.from_bytes(data[:2], byteorder="little", signed=False)

    def encode_value(self, data: int) -> bytearray:
        """Simple encode."""
        return bytearray(data.to_bytes(2, byteorder="little", signed=False))


class NoValidationCharacteristic(CustomBaseCharacteristic):
    """Test characteristic without validation attributes."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789013"),
        name="No Validation",
        unit="",
        value_type=ValueType.INT,
        properties=[],
    )

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Simple decode without validation."""
        return 42

    def encode_value(self, data: int) -> bytearray:
        """Simple encode."""
        return bytearray([42])


class TestBaseCharacteristicValidation:
    """Test the new validation functionality in BaseCharacteristic."""

    def test_successful_parse_with_validation(self) -> None:
        """Test successful parsing when all validations pass."""
        char = ValidationHelperCharacteristic()
        data = bytearray([50, 0])  # 50 in little endian, within range 0-100

        result = char.parse_value(data)

        assert result.parse_success is True
        assert result.value == 50
        assert result.error_message == ""
        assert result.raw_data == bytes([50, 0])
        assert result.name == "Test Validation"

    def test_failed_parse_with_length_validation(self) -> None:
        """Test parsing failure when length validation fails."""
        char = ValidationHelperCharacteristic()
        data = bytearray([50])  # Only 1 byte, but expects 2

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "need 2 bytes, got 1" in result.error_message
        assert result.raw_data == bytes([50])

    def test_parse_with_decode_error(self) -> None:
        """Test parsing when decode_value raises an exception."""
        char = ValidationHelperCharacteristic()
        data = bytearray([200, 0])  # 200 is out of range 0-100

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Invalid value: 200" in str(result.error_message)

    def test_range_validation_failure_min(self) -> None:
        """Test that minimum value validation failures are handled
        correctly."""

        class MinValueCharacteristic(CustomBaseCharacteristic):
            min_value: int | float | None = 10
            max_value: int | float | None = 100

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789014"),
                name="Min Value Test",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return 5  # Below min_value of 10

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MinValueCharacteristic()
        data = bytearray([1, 2])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Invalid value: 5" in result.error_message

    def test_type_validation_failure(self) -> None:
        """Test that type validation failures are handled correctly."""

        class TypeValidationCharacteristic(CustomBaseCharacteristic):
            expected_type: type | None = float

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789015"),
                name="Type Test",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )

            def decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None
            ) -> int:  # Returns int but expects float
                return 42

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = TypeValidationCharacteristic()
        data = bytearray([1, 2])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "expected type float, got int" in result.error_message

    def test_no_validation_never_fails(self) -> None:
        """Test that characteristics without validation attributes never fail."""
        char = NoValidationCharacteristic()
        data = bytearray([1, 2, 3, 4, 5])  # Any data should work

        result = char.parse_value(data)

        assert result.parse_success is True
        assert result.value == 42  # NoValidationCharacteristic always returns 42

    def test_min_length_validation(self) -> None:
        """Test minimum length validation."""

        class MinLengthCharacteristic(CustomBaseCharacteristic):
            min_length: int | None = 3

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789016"),
                name="Min Length Test",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return len(data)

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MinLengthCharacteristic()

        # Test with too short data
        result = char.parse_value(bytearray([1, 2]))  # 2 bytes < min_length 3
        assert result.parse_success is False
        assert "need 3 bytes, got 2" in result.error_message

        # Test with sufficient data
        result = char.parse_value(bytearray([1, 2, 3, 4]))  # 4 bytes >= min_length 3
        assert result.parse_success is True
        assert result.value == 4

    def test_max_length_validation(self) -> None:
        """Test maximum length validation."""

        class MaxLengthCharacteristic(CustomBaseCharacteristic):
            max_length: int | None = 3

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789017"),
                name="Max Length Test",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return len(data)

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MaxLengthCharacteristic()

        # Test with too long data
        result = char.parse_value(bytearray([1, 2, 3, 4]))  # 4 bytes > max_length 3
        assert result.parse_success is False
        assert "Maximum 3 bytes allowed, got 4" in result.error_message

        # Test with acceptable data
        result = char.parse_value(bytearray([1, 2]))  # 2 bytes <= max_length 3
        assert result.parse_success is True
        assert result.value == 2

    def test_decode_value_exception_handling(self) -> None:
        """Test that exceptions from decode_value are properly handled."""

        class ExceptionCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789018"),
                name="Exception Test",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                raise ValueError("Custom decode error")

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = ExceptionCharacteristic()
        data = bytearray([1, 2])

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert "Custom decode error" in result.error_message

    def test_struct_error_handling(self) -> None:
        """Test that struct.error exceptions are properly handled."""
        import struct

        class StructErrorCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789019"),
                name="Struct Error Test",
                unit="",
                value_type=ValueType.INT,
                properties=[],
            )

            def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                # This will raise struct.error due to insufficient data
                return int(struct.unpack("<I", data)[0])  # Needs 4 bytes for uint32

            def encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = StructErrorCharacteristic()
        data = bytearray([1, 2])  # Only 2 bytes, but struct expects 4

        result = char.parse_value(data)

        assert result.parse_success is False
        assert result.value is None
        assert result.error_message is not None  # Should contain struct error message
