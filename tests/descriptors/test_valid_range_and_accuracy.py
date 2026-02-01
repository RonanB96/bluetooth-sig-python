"""Tests for Valid Range and Accuracy descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ValidRangeAndAccuracyDescriptor
from bluetooth_sig.gatt.descriptors.valid_range_and_accuracy import ValidRangeAndAccuracyData


class TestValidRangeAndAccuracyDescriptor:
    """Test Valid Range and Accuracy descriptor functionality."""

    def test_parse_valid_range_and_accuracy(self) -> None:
        """Test parsing valid range and accuracy."""
        vra = ValidRangeAndAccuracyDescriptor()
        # Min: 0x0000, Max: 0xFFFF, Accuracy: 0x0001
        data = b"\x00\x00\xff\xff\x01\x00"

        result = vra.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, ValidRangeAndAccuracyData)
        assert result.value.min_value == 0x0000
        assert result.value.max_value == 0xFFFF
        assert result.value.accuracy == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing valid range and accuracy with invalid length."""
        vra = ValidRangeAndAccuracyDescriptor()
        data = b"\x00\x00\xff\xff"  # Too short

        result = vra.parse_value(data)
        assert result.parse_success is False
        assert "need 2 bytes, got 0" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Valid Range and Accuracy has correct UUID."""
        vra = ValidRangeAndAccuracyDescriptor()
        assert str(vra.uuid) == "00002911-0000-1000-8000-00805F9B34FB"
