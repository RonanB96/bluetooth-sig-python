"""Tests for Number of Digitals descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import NumberOfDigitalsDescriptor
from bluetooth_sig.gatt.descriptors.number_of_digitals import NumberOfDigitalsData


class TestNumberOfDigitalsDescriptor:
    """Test Number of Digitals descriptor functionality."""

    def test_parse_number_of_digitals(self) -> None:
        """Test parsing number of digitals."""
        nod = NumberOfDigitalsDescriptor()
        data = b"\x02"  # 2 digitals (1 byte)

        result = nod.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, NumberOfDigitalsData)
        assert result.value.number_of_digitals == 0x02

    def test_parse_invalid_length(self) -> None:
        """Test parsing number of digitals with invalid length."""
        nod = NumberOfDigitalsDescriptor()
        data = b"\x02\x00"  # Too long (2 bytes instead of 1)

        result = nod.parse_value(data)
        assert result.parse_success is False
        assert "Number of Digitals data must be exactly 1 byte" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Number of Digitals has correct UUID."""
        nod = NumberOfDigitalsDescriptor()
        assert str(nod.uuid) == "00002909-0000-1000-8000-00805F9B34FB"
