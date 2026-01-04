"""Tests for BaseCharacteristic validation attributes functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
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
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Simple decode - just parse as uint16."""
        if len(data) < 2:
            raise ValueError("Need at least 2 bytes")
        return int.from_bytes(data[:2], byteorder="little", signed=False)

    def _encode_value(self, data: int) -> bytearray:
        """Simple encode."""
        return bytearray(data.to_bytes(2, byteorder="little", signed=False))


class NoValidationCharacteristic(CustomBaseCharacteristic):
    """Test characteristic without validation attributes."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789013"),
        name="No Validation",
        unit="",
        value_type=ValueType.INT,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        """Simple decode without validation."""
        return 42

    def _encode_value(self, data: int) -> bytearray:
        """Simple encode."""
        return bytearray([42])


class TestBaseCharacteristicValidation:
    """Test the new validation functionality in BaseCharacteristic."""

    def test_successful_parse_with_validation(self) -> None:
        """Test successful parsing when all validations pass."""
        char = ValidationHelperCharacteristic()
        data = bytearray([50, 0])  # 50 in little endian, within range 0-100

        value = char.parse_value(data)

        assert value == 50
        # Check last_parsed for debugging info
        assert char.last_parsed is not None
        assert char.last_parsed.raw_data == bytes([50, 0])
        assert char.last_parsed.characteristic._info.name == "Test Validation"

    def test_failed_parse_with_length_validation(self) -> None:
        """Test parsing failure when length validation fails."""
        char = ValidationHelperCharacteristic()
        data = bytearray([50])  # Only 1 byte, but expects 2

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert "expected exactly 2 bytes, got 1" in str(exc_info.value)
        assert exc_info.value.raw_data == bytes([50])

    def test_parse_with_decode_error(self) -> None:
        """Test parsing when decode_value raises an exception."""
        char = ValidationHelperCharacteristic()
        data = bytearray([200, 0])  # 200 is out of range 0-100

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert "Value 200 is above maximum 100" in str(exc_info.value)

    def test_range_validation_failure_min(self) -> None:
        """Test that minimum value validation failures are handled
        correctly.
        """

        class MinValueCharacteristic(CustomBaseCharacteristic):
            min_value: int | float | None = 10
            max_value: int | float | None = 100

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789014"),
                name="Min Value Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return 5  # Below min_value of 10

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MinValueCharacteristic()
        data = bytearray([1, 2])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert "Value 5 is below minimum 10" in str(exc_info.value)

    def test_type_validation_failure(self) -> None:
        """Test that type validation failures are handled correctly."""

        class TypeValidationCharacteristic(CustomBaseCharacteristic):
            expected_type: type | None = float

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789015"),
                name="Type Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None
            ) -> int:  # Returns int but expects float
                return 42

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = TypeValidationCharacteristic()
        data = bytearray([1, 2])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert "expected float, got int" in str(exc_info.value)

    def test_no_validation_never_fails(self) -> None:
        """Test that characteristics without validation attributes never fail."""
        char = NoValidationCharacteristic()
        data = bytearray([1, 2, 3, 4, 5])  # Any data should work

        value = char.parse_value(data)

        assert value == 42  # NoValidationCharacteristic always returns 42

    def test_min_length_validation(self) -> None:
        """Test minimum length validation."""

        class MinLengthCharacteristic(CustomBaseCharacteristic):
            min_length: int | None = 3

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789016"),
                name="Min Length Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return len(data)

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MinLengthCharacteristic()

        # Test with too short data
        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(bytearray([1, 2]))  # 2 bytes < min_length 3
        assert "expected at least 3 bytes, got 2" in str(exc_info.value)

        # Test with sufficient data
        value = char.parse_value(bytearray([1, 2, 3, 4]))  # 4 bytes >= min_length 3
        assert value == 4

    def test_max_length_validation(self) -> None:
        """Test maximum length validation."""

        class MaxLengthCharacteristic(CustomBaseCharacteristic):
            max_length: int | None = 3

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789017"),
                name="Max Length Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                return len(data)

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = MaxLengthCharacteristic()

        # Test with too long data
        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(bytearray([1, 2, 3, 4]))  # 4 bytes > max_length 3
        assert "expected at most 3 bytes, got 4" in str(exc_info.value)

        # Test with acceptable data
        value = char.parse_value(bytearray([1, 2]))  # 2 bytes <= max_length 3
        assert value == 2

    def test_decode_value_exception_handling(self) -> None:
        """Test that exceptions from decode_value are properly handled."""

        class ExceptionCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789018"),
                name="Exception Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                raise ValueError("Custom decode error")

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = ExceptionCharacteristic()
        data = bytearray([1, 2])

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert "Custom decode error" in str(exc_info.value)

    def test_struct_error_handling(self) -> None:
        """Test that struct.error exceptions are properly handled."""
        import struct

        class StructErrorCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789019"),
                name="Struct Error Test",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
                # This will raise struct.error due to insufficient data
                return int(struct.unpack("<I", data)[0])  # Needs 4 bytes for uint32

            def _encode_value(self, data: int) -> bytearray:
                return bytearray()

        char = StructErrorCharacteristic()
        data = bytearray([1, 2])  # Only 2 bytes, but struct expects 4

        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        # Should contain struct error message
        assert exc_info.value.raw_data == bytes([1, 2])

    def test_build_value_validation(self) -> None:
        """Test that build_value performs validation and raises errors."""
        from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError

        char = ValidationHelperCharacteristic()

        # Test successful build
        result = char.build_value(50)  # Within range 0-100
        assert result == bytearray([50, 0])

        # Test range validation failure
        with pytest.raises(CharacteristicEncodeError, match="150.*maximum"):
            char.build_value(150)  # Above max_value

        # Test type validation failure
        with pytest.raises(CharacteristicEncodeError, match="expected int"):
            char.build_value("not an int")  # Wrong type


class TestValidationControl:
    """Test the validate parameter for enabling/disabling validation."""

    def test_validation_enabled_by_default(self) -> None:
        """Test that validation is enabled by default."""
        char = ValidationHelperCharacteristic()

        # Out-of-range value should fail with default validation
        data = bytearray([200, 0])  # 200 is out of range 0-100
        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(data)

        assert "Value 200 is above maximum 100" in str(exc_info.value)

    def test_validation_can_be_disabled(self) -> None:
        """Test that validation can be explicitly disabled per-call."""
        char = ValidationHelperCharacteristic()

        # Out-of-range value should succeed when validation disabled
        data = bytearray([200, 0])  # 200 is out of range 0-100
        value = char.parse_value(data, validate=False)

        assert value == 200

    def test_disabled_validation_skips_length_check(self) -> None:
        """Test that disabled validation skips length validation."""
        char = ValidationHelperCharacteristic()

        # Wrong length should succeed when validation disabled
        # Note: decode_value will still raise if it needs more bytes
        data = bytearray([50, 0, 99])  # 3 bytes instead of expected 2
        value = char.parse_value(data, validate=False)

        assert value == 50  # Should still decode the first 2 bytes

    def test_disabled_validation_skips_type_check(self) -> None:
        """Test that disabled validation skips type validation."""

        class TypeMismatchCharacteristic(CustomBaseCharacteristic):
            expected_type: type | None = int

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789020"),
                name="Type Mismatch",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> str:
                # Returns string but expected_type is int
                return "not an int"

            def _encode_value(self, data: str) -> bytearray:
                return bytearray([42])

        # With validation enabled (default) - should fail
        char = TypeMismatchCharacteristic()
        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(bytearray([1, 2]))
        assert "expected int, got str" in str(exc_info.value)

        # With validation disabled - should succeed
        value = char.parse_value(bytearray([1, 2]), validate=False)
        assert value == "not an int"

    def test_disabled_validation_in_build_value(self) -> None:
        """Test that disabled validation affects build_value as well."""
        char = ValidationHelperCharacteristic()

        # Out-of-range value should succeed in build when validation disabled
        result = char.build_value(200, validate=False)  # Above max_value of 100
        assert result == bytearray([200, 0])

    def test_validation_control_with_validation_config(self) -> None:
        """Test that validate parameter works alongside ValidationConfig."""
        from bluetooth_sig.gatt.characteristics.base import ValidationConfig

        # Both validation control and constraints can be specified
        char = ValidationHelperCharacteristic(validation=ValidationConfig(min_value=10, max_value=50))

        # Even with tighter constraints in ValidationConfig, validation can be disabled per-call
        data = bytearray([200, 0])  # Out of range
        value = char.parse_value(data, validate=False)

        assert value == 200

    def test_validation_separate_calls(self) -> None:
        """Test that validation control is per-call, not global."""
        char = ValidationHelperCharacteristic()

        data = bytearray([200, 0])  # Out of range

        # First call with validation should fail
        with pytest.raises(CharacteristicParseError):
            char.parse_value(data, validate=True)

        # Second call without validation should succeed
        value = char.parse_value(data, validate=False)
        assert value == 200
