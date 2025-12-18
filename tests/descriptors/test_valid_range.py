"""Tests for Valid Range descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ValidRangeDescriptor
from bluetooth_sig.gatt.descriptors.valid_range import ValidRangeData


class TestValidRangeDescriptor:
    """Test Valid Range descriptor functionality."""

    def test_parse_valid_range(self) -> None:
        """Test parsing valid range descriptor."""
        valid_range = ValidRangeDescriptor()
        data = b"\x00\x00\xff\xff"  # Min: 0, Max: 65535

        result = valid_range.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ValidRangeData)
        assert result.value.min_value == 0
        assert result.value.max_value == 65535

    def test_parse_invalid_length(self) -> None:
        """Test parsing valid range with invalid length."""
        valid_range = ValidRangeDescriptor()
        data = b"\x00\x00"  # Too short

        result = valid_range.parse_value(data)
        assert not result.parse_success
        assert "Valid Range data expected 4 bytes, got 2" in result.error_message

    def test_validate_value_in_range(self) -> None:
        """Test validating a value within range."""
        valid_range = ValidRangeDescriptor()
        data = b"\x0a\x00\x64\x00"  # Min: 10, Max: 100

        result = valid_range.parse_value(data)
        assert result.parse_success

        # Test validation
        assert valid_range.is_value_in_range(data, 50) is True
        assert valid_range.is_value_in_range(data, 5) is False  # Below min
        assert valid_range.is_value_in_range(data, 150) is False  # Above max

    def test_uuid_resolution(self) -> None:
        """Test that Valid Range has correct UUID."""
        valid_range = ValidRangeDescriptor()
        assert str(valid_range.uuid) == "00002906-0000-1000-8000-00805F9B34FB"
