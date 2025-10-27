"""Test cases for data parser utilities."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics.utils.data_parser import DataParser
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError


class TestDataParserInt8:
    """Test 8-bit integer parsing and encoding."""

    def test_parse_unsigned_int8(self) -> None:
        """Test parsing unsigned 8-bit integers."""
        data = bytearray([0x00, 0x7F, 0x80, 0xFF])
        assert DataParser.parse_int8(data, 0, signed=False) == 0
        assert DataParser.parse_int8(data, 1, signed=False) == 127
        assert DataParser.parse_int8(data, 2, signed=False) == 128
        assert DataParser.parse_int8(data, 3, signed=False) == 255

    def test_parse_signed_int8(self) -> None:
        """Test parsing signed 8-bit integers."""
        data = bytearray([0x00, 0x7F, 0x80, 0xFF])
        assert DataParser.parse_int8(data, 0, signed=True) == 0
        assert DataParser.parse_int8(data, 1, signed=True) == 127
        assert DataParser.parse_int8(data, 2, signed=True) == -128
        assert DataParser.parse_int8(data, 3, signed=True) == -1

    def test_parse_int8_insufficient_data(self) -> None:
        """Test parsing 8-bit integer with insufficient data."""
        data = bytearray([])
        with pytest.raises(InsufficientDataError):
            DataParser.parse_int8(data, 0)

    def test_encode_unsigned_int8(self) -> None:
        """Test encoding unsigned 8-bit integers."""
        assert DataParser.encode_int8(0, signed=False) == bytearray([0x00])
        assert DataParser.encode_int8(127, signed=False) == bytearray([0x7F])
        assert DataParser.encode_int8(255, signed=False) == bytearray([0xFF])

    def test_encode_signed_int8(self) -> None:
        """Test encoding signed 8-bit integers."""
        assert DataParser.encode_int8(0, signed=True) == bytearray([0x00])
        assert DataParser.encode_int8(127, signed=True) == bytearray([0x7F])
        assert DataParser.encode_int8(-128, signed=True) == bytearray([0x80])
        assert DataParser.encode_int8(-1, signed=True) == bytearray([0xFF])

    def test_encode_int8_range_errors(self) -> None:
        """Test encoding 8-bit integer range validation."""
        # Unsigned range errors
        with pytest.raises(ValueRangeError):
            DataParser.encode_int8(-1, signed=False)
        with pytest.raises(ValueRangeError):
            DataParser.encode_int8(256, signed=False)

        # Signed range errors
        with pytest.raises(ValueRangeError):
            DataParser.encode_int8(-129, signed=True)
        with pytest.raises(ValueRangeError):
            DataParser.encode_int8(128, signed=True)


class TestDataParserInt16:
    """Test 16-bit integer parsing and encoding."""

    def test_parse_unsigned_int16_little_endian(self) -> None:
        """Test parsing unsigned 16-bit integers (little-endian)."""
        data = bytearray([0x00, 0x00, 0xFF, 0x7F, 0x00, 0x80, 0xFF, 0xFF])
        assert DataParser.parse_int16(data, 0, signed=False, endian="little") == 0
        assert DataParser.parse_int16(data, 2, signed=False, endian="little") == 32767
        assert DataParser.parse_int16(data, 4, signed=False, endian="little") == 32768
        assert DataParser.parse_int16(data, 6, signed=False, endian="little") == 65535

    def test_parse_unsigned_int16_big_endian(self) -> None:
        """Test parsing unsigned 16-bit integers (big-endian)."""
        data = bytearray([0x00, 0x00, 0x7F, 0xFF, 0x80, 0x00, 0xFF, 0xFF])
        assert DataParser.parse_int16(data, 0, signed=False, endian="big") == 0
        assert DataParser.parse_int16(data, 2, signed=False, endian="big") == 32767
        assert DataParser.parse_int16(data, 4, signed=False, endian="big") == 32768
        assert DataParser.parse_int16(data, 6, signed=False, endian="big") == 65535

    def test_parse_signed_int16_little_endian(self) -> None:
        """Test parsing signed 16-bit integers (little-endian)."""
        data = bytearray([0x00, 0x00, 0xFF, 0x7F, 0x00, 0x80, 0xFF, 0xFF])
        assert DataParser.parse_int16(data, 0, signed=True, endian="little") == 0
        assert DataParser.parse_int16(data, 2, signed=True, endian="little") == 32767
        assert DataParser.parse_int16(data, 4, signed=True, endian="little") == -32768
        assert DataParser.parse_int16(data, 6, signed=True, endian="little") == -1

    def test_parse_int16_insufficient_data(self) -> None:
        """Test parsing 16-bit integer with insufficient data."""
        data = bytearray([0x00])
        with pytest.raises(InsufficientDataError):
            DataParser.parse_int16(data, 0)

    def test_encode_unsigned_int16(self) -> None:
        """Test encoding unsigned 16-bit integers."""
        assert DataParser.encode_int16(0, signed=False) == bytearray([0x00, 0x00])
        assert DataParser.encode_int16(32767, signed=False) == bytearray([0xFF, 0x7F])
        assert DataParser.encode_int16(65535, signed=False) == bytearray([0xFF, 0xFF])

    def test_encode_signed_int16(self) -> None:
        """Test encoding signed 16-bit integers."""
        assert DataParser.encode_int16(0, signed=True) == bytearray([0x00, 0x00])
        assert DataParser.encode_int16(32767, signed=True) == bytearray([0xFF, 0x7F])
        assert DataParser.encode_int16(-32768, signed=True) == bytearray([0x00, 0x80])
        assert DataParser.encode_int16(-1, signed=True) == bytearray([0xFF, 0xFF])

    def test_encode_int16_big_endian(self) -> None:
        """Test encoding 16-bit integers (big-endian)."""
        assert DataParser.encode_int16(32767, signed=False, endian="big") == bytearray([0x7F, 0xFF])
        assert DataParser.encode_int16(-1, signed=True, endian="big") == bytearray([0xFF, 0xFF])

    def test_encode_int16_range_errors(self) -> None:
        """Test encoding 16-bit integer range validation."""
        # Unsigned range errors
        with pytest.raises(ValueRangeError):
            DataParser.encode_int16(-1, signed=False)
        with pytest.raises(ValueRangeError):
            DataParser.encode_int16(65536, signed=False)

        # Signed range errors
        with pytest.raises(ValueRangeError):
            DataParser.encode_int16(-32769, signed=True)
        with pytest.raises(ValueRangeError):
            DataParser.encode_int16(32768, signed=True)


class TestDataParserInt32:
    """Test 32-bit integer parsing and encoding."""

    def test_parse_unsigned_int32_little_endian(self) -> None:
        """Test parsing unsigned 32-bit integers (little-endian)."""
        data = bytearray([0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x7F, 0x00, 0x00, 0x00, 0x80])
        assert DataParser.parse_int32(data, 0, signed=False, endian="little") == 0
        assert DataParser.parse_int32(data, 4, signed=False, endian="little") == 2147483647
        assert DataParser.parse_int32(data, 8, signed=False, endian="little") == 2147483648

    def test_parse_signed_int32_little_endian(self) -> None:
        """Test parsing signed 32-bit integers (little-endian)."""
        data = bytearray([0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x7F, 0x00, 0x00, 0x00, 0x80])
        assert DataParser.parse_int32(data, 0, signed=True, endian="little") == 0
        assert DataParser.parse_int32(data, 4, signed=True, endian="little") == 2147483647
        assert DataParser.parse_int32(data, 8, signed=True, endian="little") == -2147483648

    def test_parse_int32_insufficient_data(self) -> None:
        """Test parsing 32-bit integer with insufficient data."""
        data = bytearray([0x00, 0x00, 0x00])
        with pytest.raises(InsufficientDataError):
            DataParser.parse_int32(data, 0)

    def test_encode_unsigned_int32(self) -> None:
        """Test encoding unsigned 32-bit integers."""
        assert DataParser.encode_int32(0, signed=False) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert DataParser.encode_int32(2147483647, signed=False) == bytearray([0xFF, 0xFF, 0xFF, 0x7F])

    def test_encode_signed_int32(self) -> None:
        """Test encoding signed 32-bit integers."""
        assert DataParser.encode_int32(0, signed=True) == bytearray([0x00, 0x00, 0x00, 0x00])
        assert DataParser.encode_int32(2147483647, signed=True) == bytearray([0xFF, 0xFF, 0xFF, 0x7F])
        assert DataParser.encode_int32(-2147483648, signed=True) == bytearray([0x00, 0x00, 0x00, 0x80])

    def test_encode_int32_range_errors(self) -> None:
        """Test encoding 32-bit integer range validation."""
        # Unsigned range errors
        with pytest.raises(ValueRangeError):
            DataParser.encode_int32(-1, signed=False)
        with pytest.raises(ValueRangeError):
            DataParser.encode_int32(4294967296, signed=False)

        # Signed range errors
        with pytest.raises(ValueRangeError):
            DataParser.encode_int32(-2147483649, signed=True)
        with pytest.raises(ValueRangeError):
            DataParser.encode_int32(2147483648, signed=True)


class TestDataParserFloat:
    """Test IEEE-754 float parsing and encoding."""

    def test_parse_float32(self) -> None:
        """Test parsing IEEE-754 32-bit floats."""
        # Test known values
        data = bytearray(struct.pack("<f", 3.14159))
        result = DataParser.parse_float32(data, 0)
        assert abs(result - 3.14159) < 1e-6

        # Test zero
        data = bytearray(struct.pack("<f", 0.0))
        result = DataParser.parse_float32(data, 0)
        assert result == 0.0

        # Test negative
        data = bytearray(struct.pack("<f", -123.456))
        result = DataParser.parse_float32(data, 0)
        assert abs(result - (-123.456)) < 1e-5  # Allow for IEEE-754 precision limits

    def test_parse_float64(self) -> None:
        """Test parsing IEEE-754 64-bit doubles."""
        # Test known values
        data = bytearray(struct.pack("<d", 3.141592653589793))
        result = DataParser.parse_float64(data, 0)
        assert abs(result - 3.141592653589793) < 1e-15

        # Test zero
        data = bytearray(struct.pack("<d", 0.0))
        result = DataParser.parse_float64(data, 0)
        assert result == 0.0

    def test_parse_float_insufficient_data(self) -> None:
        """Test parsing floats with insufficient data."""
        # Float32
        data = bytearray([0x00, 0x00, 0x00])  # Only 3 bytes
        with pytest.raises(InsufficientDataError):
            DataParser.parse_float32(data, 0)

        # Float64
        data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Only 7 bytes
        with pytest.raises(InsufficientDataError):
            DataParser.parse_float64(data, 0)

    def test_encode_float32(self) -> None:
        """Test encoding IEEE-754 32-bit floats."""
        result = DataParser.encode_float32(3.14159)
        expected = bytearray(struct.pack("<f", 3.14159))
        assert result == expected

    def test_encode_float64(self) -> None:
        """Test encoding IEEE-754 64-bit doubles."""
        result = DataParser.encode_float64(3.141592653589793)
        expected = bytearray(struct.pack("<d", 3.141592653589793))
        assert result == expected

    def test_float_roundtrip(self) -> None:
        """Test float encode/decode roundtrip."""
        test_values = [0.0, 1.0, -1.0, 3.14159, -123.456, 1e6, 1e-6]

        # Float32 roundtrip
        for value in test_values:
            encoded = DataParser.encode_float32(value)
            decoded = DataParser.parse_float32(encoded, 0)
            assert abs(decoded - value) < max(abs(value) * 1e-6, 1e-6)

        # Float64 roundtrip
        for value in test_values:
            encoded = DataParser.encode_float64(value)
            decoded = DataParser.parse_float64(encoded, 0)
            assert abs(decoded - value) < max(abs(value) * 1e-15, 1e-15)


class TestDataParserString:
    """Test string parsing utilities."""

    def test_parse_utf8_string(self) -> None:
        """Test parsing UTF-8 strings."""
        # Basic ASCII
        data = bytearray(b"Hello")
        assert DataParser.parse_utf8_string(data) == "Hello"

        # With null termination
        data = bytearray(b"Hello\x00")
        assert DataParser.parse_utf8_string(data) == "Hello"

        # UTF-8 characters
        data = bytearray("Café".encode())
        assert DataParser.parse_utf8_string(data) == "Café"

        # Empty string
        data = bytearray()
        assert DataParser.parse_utf8_string(data) == ""

        # Only null bytes
        data = bytearray(b"\x00\x00\x00")
        assert DataParser.parse_utf8_string(data) == ""

    def test_parse_utf8_string_error_handling(self) -> None:
        """Test UTF-8 string parsing with invalid bytes."""
        # Invalid UTF-8 sequence (should be replaced)
        data = bytearray([0xFF, 0xFE, 0xFD])
        result = DataParser.parse_utf8_string(data)
        # Should contain replacement characters
        assert "�" in result or result == ""  # Depends on error handling


class TestDataParserVariableLength:
    """Test variable length data parsing."""

    def test_parse_variable_length_valid(self) -> None:
        """Test parsing variable length data within bounds."""
        data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        result = DataParser.parse_variable_length(data, 3, 10)
        assert result == bytes([0x01, 0x02, 0x03, 0x04, 0x05])

    def test_parse_variable_length_minimum(self) -> None:
        """Test parsing variable length data at minimum bound."""
        data = bytearray([0x01, 0x02, 0x03])
        result = DataParser.parse_variable_length(data, 3, 10)
        assert result == bytes([0x01, 0x02, 0x03])

    def test_parse_variable_length_maximum(self) -> None:
        """Test parsing variable length data at maximum bound."""
        data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05])
        result = DataParser.parse_variable_length(data, 1, 5)
        assert result == bytes([0x01, 0x02, 0x03, 0x04, 0x05])

    def test_parse_variable_length_too_short(self) -> None:
        """Test parsing variable length data that's too short."""
        data = bytearray([0x01, 0x02])
        with pytest.raises(ValueError, match="Data too short"):
            DataParser.parse_variable_length(data, 3, 10)

    def test_parse_variable_length_too_long(self) -> None:
        """Test parsing variable length data that's too long."""
        data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
        with pytest.raises(ValueError, match="Data too long"):
            DataParser.parse_variable_length(data, 1, 5)
