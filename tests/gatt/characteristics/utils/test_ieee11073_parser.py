"""Test cases for IEEE-11073 parser utilities."""

from __future__ import annotations

import math
import struct
from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics.utils.ieee11073_parser import IEEE11073Parser
from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError


class TestIEEE11073SFLOATParser:
    """Test IEEE-11073 SFLOAT (16-bit) parsing and encoding."""

    def test_parse_basic_positive_value(self) -> None:
        """Test parsing basic positive SFLOAT value."""
        # 1.0 as SFLOAT: mantissa=10, exponent=-1 (10 * 10^-1 = 1.0)
        data = bytearray([0x0A, 0x70])  # 0x700A
        result = IEEE11073Parser.parse_sfloat(data)
        assert abs(result - 1.0) < 1e-6

    def test_parse_basic_negative_value(self) -> None:
        """Test parsing basic negative SFLOAT value."""
        # -1.0 as SFLOAT: mantissa=-10 (0xFF6), exponent=-1
        data = bytearray([0xF6, 0x7F])  # 0x7FF6
        result = IEEE11073Parser.parse_sfloat(data)
        assert abs(result - (-1.0)) < 1e-6

    def test_parse_special_values(self) -> None:
        """Test parsing SFLOAT special values."""
        # NaN
        data = bytearray([0xFF, 0x07])  # 0x07FF
        assert math.isnan(IEEE11073Parser.parse_sfloat(data))

        # NRes (Not a valid result) - treated as NaN
        data = bytearray([0x00, 0x08])  # 0x0800
        assert math.isnan(IEEE11073Parser.parse_sfloat(data))

        # +Infinity
        data = bytearray([0xFE, 0x07])  # 0x07FE
        assert math.isinf(IEEE11073Parser.parse_sfloat(data))
        assert IEEE11073Parser.parse_sfloat(data) > 0

        # -Infinity
        data = bytearray([0x02, 0x08])  # 0x0802
        assert math.isinf(IEEE11073Parser.parse_sfloat(data))
        assert IEEE11073Parser.parse_sfloat(data) < 0

    def test_parse_with_offset(self) -> None:
        """Test parsing SFLOAT with offset."""
        data = bytearray([0x00, 0x00, 0x0A, 0x70])  # Leading zeros + 1.0
        result = IEEE11073Parser.parse_sfloat(data, offset=2)
        assert abs(result - 1.0) < 1e-6

    def test_parse_insufficient_data(self) -> None:
        """Test parsing SFLOAT with insufficient data."""
        data = bytearray([0x0A])  # Only 1 byte
        with pytest.raises(InsufficientDataError):
            IEEE11073Parser.parse_sfloat(data)

    def test_encode_basic_positive_value(self) -> None:
        """Test encoding basic positive SFLOAT value."""
        result = IEEE11073Parser.encode_sfloat(1.0)
        # Should be close to original value when parsed back
        parsed = IEEE11073Parser.parse_sfloat(result)
        assert abs(parsed - 1.0) < 1e-2  # Allow small encoding error

    def test_encode_basic_negative_value(self) -> None:
        """Test encoding basic negative SFLOAT value."""
        result = IEEE11073Parser.encode_sfloat(-1.0)
        parsed = IEEE11073Parser.parse_sfloat(result)
        assert abs(parsed - (-1.0)) < 1e-2

    def test_encode_special_values(self) -> None:
        """Test encoding SFLOAT special values."""
        # NaN
        result = IEEE11073Parser.encode_sfloat(float("nan"))
        assert result == bytearray([0xFF, 0x07])

        # +Infinity
        result = IEEE11073Parser.encode_sfloat(float("inf"))
        assert result == bytearray([0xFE, 0x07])

        # -Infinity
        result = IEEE11073Parser.encode_sfloat(float("-inf"))
        assert result == bytearray([0x02, 0x08])

    def test_encode_decode_roundtrip(self) -> None:
        """Test SFLOAT encode/decode roundtrip for various values."""
        test_values = [0.0, 1.0, -1.0, 10.0, -10.0, 0.1, -0.1, 123.4, -567.8]
        for value in test_values:
            encoded = IEEE11073Parser.encode_sfloat(value)
            decoded = IEEE11073Parser.parse_sfloat(encoded)
            # Allow reasonable encoding precision for SFLOAT
            assert abs(decoded - value) < max(abs(value) * 0.01, 0.01)


class TestIEEE11073FLOAT32Parser:
    """Test IEEE-11073 FLOAT32 (32-bit) parsing and encoding."""

    def test_parse_basic_positive_value(self) -> None:
        """Test parsing basic positive FLOAT32 value."""
        # 37.0 as FLOAT32: mantissa=370, exponent=-1 (370 * 10^-1 = 37.0)
        data = bytearray([0x72, 0x01, 0x00, 0x7F])  # 0x7F000172
        result = IEEE11073Parser.parse_float32(data)
        assert abs(result - 37.0) < 1e-6

    def test_parse_basic_negative_value(self) -> None:
        """Test parsing basic negative FLOAT32 value."""
        # -37.0 as FLOAT32: mantissa=-370, exponent=-1
        data = bytearray([0x8E, 0xFE, 0xFF, 0x7F])  # Negative mantissa
        result = IEEE11073Parser.parse_float32(data)
        assert abs(result - (-37.0)) < 1e-6

    def test_parse_special_values(self) -> None:
        """Test parsing FLOAT32 special values.

        Per IEEE 11073-20601 and Bluetooth GSS:
        - NaN: 0x007FFFFF (exponent=0, mantissa=0x7FFFFF)
        - +Infinity: 0x007FFFFE (exponent=0, mantissa=0x7FFFFE)
        - -Infinity: 0x00800002 (exponent=0, mantissa=0x800002)
        - NRes: 0x00800000 (exponent=0, mantissa=0x800000)
        - RFU: 0x00800001 (exponent=0, mantissa=0x800001)
        """
        # NaN
        data = bytearray([0xFF, 0xFF, 0x7F, 0x00])  # 0x007FFFFF
        assert math.isnan(IEEE11073Parser.parse_float32(data))

        # +Infinity (0x007FFFFE)
        data = bytearray([0xFE, 0xFF, 0x7F, 0x00])  # 0x007FFFFE
        assert math.isinf(IEEE11073Parser.parse_float32(data))
        assert IEEE11073Parser.parse_float32(data) > 0

        # -Infinity (0x00800002)
        data = bytearray([0x02, 0x00, 0x80, 0x00])  # 0x00800002
        assert math.isinf(IEEE11073Parser.parse_float32(data))
        assert IEEE11073Parser.parse_float32(data) < 0

        # NRes (Not a valid result) - 0x00800000
        data = bytearray([0x00, 0x00, 0x80, 0x00])  # 0x00800000
        assert math.isnan(IEEE11073Parser.parse_float32(data))

    def test_parse_with_offset(self) -> None:
        """Test parsing FLOAT32 with offset."""
        data = bytearray([0x00, 0x00, 0x72, 0x01, 0x00, 0x7F])  # Leading zeros + 37.0
        result = IEEE11073Parser.parse_float32(data, offset=2)
        assert abs(result - 37.0) < 1e-6

    def test_parse_insufficient_data(self) -> None:
        """Test parsing FLOAT32 with insufficient data."""
        data = bytearray([0x72, 0x01, 0x00])  # Only 3 bytes
        with pytest.raises(InsufficientDataError):
            IEEE11073Parser.parse_float32(data)

    def test_encode_basic_positive_value(self) -> None:
        """Test encoding basic positive FLOAT32 value."""
        result = IEEE11073Parser.encode_float32(37.0)
        parsed = IEEE11073Parser.parse_float32(result)
        assert abs(parsed - 37.0) < 1e-6

    def test_encode_basic_negative_value(self) -> None:
        """Test encoding basic negative FLOAT32 value."""
        result = IEEE11073Parser.encode_float32(-37.0)
        parsed = IEEE11073Parser.parse_float32(result)
        assert abs(parsed - (-37.0)) < 1e-6

    def test_encode_zero(self) -> None:
        """Test encoding zero value."""
        result = IEEE11073Parser.encode_float32(0.0)
        assert result == bytearray([0x00, 0x00, 0x00, 0x00])

    def test_encode_special_values(self) -> None:
        """Test encoding FLOAT32 special values.

        Per IEEE 11073-20601 and Bluetooth GSS:
        - NaN: 0x007FFFFF
        - +Infinity: 0x007FFFFE
        - -Infinity: 0x00800002
        """
        # NaN
        result = IEEE11073Parser.encode_float32(float("nan"))
        assert result == bytearray([0xFF, 0xFF, 0x7F, 0x00])

        # +Infinity (0x007FFFFE in little-endian)
        result = IEEE11073Parser.encode_float32(float("inf"))
        assert result == bytearray([0xFE, 0xFF, 0x7F, 0x00])

        # -Infinity (0x00800002 in little-endian)
        result = IEEE11073Parser.encode_float32(float("-inf"))
        assert result == bytearray([0x02, 0x00, 0x80, 0x00])

    def test_encode_decode_roundtrip(self) -> None:
        """Test FLOAT32 encode/decode roundtrip for various values."""
        test_values = [0.0, 1.0, -1.0, 37.0, -37.0, 98.6, -273.15, 1234.567, -9876.543]
        for value in test_values:
            encoded = IEEE11073Parser.encode_float32(value)
            decoded = IEEE11073Parser.parse_float32(encoded)
            # FLOAT32 should have better precision than SFLOAT
            assert abs(decoded - value) < max(abs(value) * 0.001, 0.001)

    def test_encode_large_value_precision_loss(self) -> None:
        """Test encoding very large value may lose precision but shouldn't crash."""
        # Very large values may lose precision but should still encode
        very_large_value = 1e10
        encoded = IEEE11073Parser.encode_float32(very_large_value)
        decoded = IEEE11073Parser.parse_float32(encoded)
        # Should be approximately the same order of magnitude
        assert decoded > 1e9  # At least close to the original magnitude


class TestIEEE11073TimestampParser:
    """Test IEEE-11073 timestamp parsing and encoding."""

    def test_parse_basic_timestamp(self) -> None:
        """Test parsing basic timestamp."""
        # 2023-12-25 14:30:45
        data = bytearray(struct.pack("<HBBBBB", 2023, 12, 25, 14, 30, 45))
        result = IEEE11073Parser.parse_timestamp(data, 0)
        assert result == datetime(2023, 12, 25, 14, 30, 45)

    def test_parse_timestamp_with_offset(self) -> None:
        """Test parsing timestamp with offset."""
        # Leading bytes + 2023-12-25 14:30:45
        data = bytearray([0x00, 0x00]) + bytearray(struct.pack("<HBBBBB", 2023, 12, 25, 14, 30, 45))
        result = IEEE11073Parser.parse_timestamp(data, 2)
        assert result == datetime(2023, 12, 25, 14, 30, 45)

    def test_parse_timestamp_insufficient_data(self) -> None:
        """Test parsing timestamp with insufficient data."""
        data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])  # Only 6 bytes
        with pytest.raises(InsufficientDataError):
            IEEE11073Parser.parse_timestamp(data, 0)

    def test_encode_basic_timestamp(self) -> None:
        """Test encoding basic timestamp."""
        timestamp = datetime(2023, 12, 25, 14, 30, 45)
        result = IEEE11073Parser.encode_timestamp(timestamp)
        expected = bytearray(struct.pack("<HBBBBB", 2023, 12, 25, 14, 30, 45))
        assert result == expected

    def test_encode_timestamp_validation_errors(self) -> None:
        """Test timestamp encoding validation errors."""
        # Year too early (before 1582)
        with pytest.raises(ValueRangeError):
            IEEE11073Parser.encode_timestamp(datetime(1500, 1, 1, 0, 0, 0))

        # Invalid month
        with pytest.raises(ValueError):
            datetime(2023, 13, 1, 0, 0, 0)  # datetime constructor will catch this

        # Hour out of range (25)
        with pytest.raises(ValueError):
            datetime(2023, 1, 1, 25, 0, 0)  # datetime constructor will catch this

    def test_encode_decode_timestamp_roundtrip(self) -> None:
        """Test timestamp encode/decode roundtrip."""
        test_timestamps = [
            datetime(2023, 1, 1, 0, 0, 0),
            datetime(2023, 12, 31, 23, 59, 59),
            datetime(2000, 2, 29, 12, 30, 45),  # Leap year
            datetime(1582, 10, 15, 12, 0, 0),  # Minimum IEEE-11073 date
        ]
        for timestamp in test_timestamps:
            encoded = IEEE11073Parser.encode_timestamp(timestamp)
            decoded = IEEE11073Parser.parse_timestamp(encoded, 0)
            assert decoded == timestamp

    def test_encode_edge_case_timestamps(self) -> None:
        """Test encoding edge case timestamps."""
        # Minimum valid year (1582)
        timestamp = datetime(1582, 1, 1, 0, 0, 0)
        result = IEEE11073Parser.encode_timestamp(timestamp)
        decoded = IEEE11073Parser.parse_timestamp(result, 0)
        assert decoded == timestamp

        # End of year
        timestamp = datetime(2023, 12, 31, 23, 59, 59)
        result = IEEE11073Parser.encode_timestamp(timestamp)
        decoded = IEEE11073Parser.parse_timestamp(result, 0)
        assert decoded == timestamp
