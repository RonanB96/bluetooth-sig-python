"""Tests for Characteristic Aggregate Format descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CharacteristicAggregateFormatDescriptor
from bluetooth_sig.gatt.descriptors.characteristic_aggregate_format import CharacteristicAggregateFormatData


class TestCharacteristicAggregateFormatDescriptor:
    """Test Characteristic Aggregate Format descriptor functionality."""

    def test_parse_aggregate_format(self) -> None:
        """Test parsing aggregate format data."""
        caf = CharacteristicAggregateFormatDescriptor()
        # Two handles: 0x0001, 0x0002
        data = b"\x01\x00\x02\x00"

        result = caf.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicAggregateFormatData)
        assert result.value.attribute_handles == [0x0001, 0x0002]

    def test_parse_single_handle(self) -> None:
        """Test parsing aggregate format with single handle."""
        caf = CharacteristicAggregateFormatDescriptor()
        data = b"\x01\x00"

        result = caf.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicAggregateFormatData)
        assert result.value.attribute_handles == [0x0001]

    def test_parse_invalid_length(self) -> None:
        """Test parsing aggregate format with invalid length."""
        caf = CharacteristicAggregateFormatDescriptor()
        data = b"\x01"  # Odd length (should be even)

        result = caf.parse_value(data)
        assert not result.parse_success
        assert "must have even length" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic Aggregate Format has correct UUID."""
        caf = CharacteristicAggregateFormatDescriptor()
        assert str(caf.uuid) == "00002905-0000-1000-8000-00805F9B34FB"
