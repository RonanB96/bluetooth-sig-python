"""Tests for Characteristic Extended Properties descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CharacteristicExtendedPropertiesDescriptor
from bluetooth_sig.gatt.descriptors.characteristic_extended_properties import CharacteristicExtendedPropertiesData


class TestCharacteristicExtendedPropertiesDescriptor:
    """Test Characteristic Extended Properties descriptor functionality."""

    def test_parse_extended_properties(self) -> None:
        """Test parsing extended properties flags."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        data = b"\x01\x00"  # Reliable Write enabled

        result = ext_props.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicExtendedPropertiesData)
        assert result.value.reliable_write is True
        assert result.value.writable_auxiliaries is False

    def test_parse_multiple_flags(self) -> None:
        """Test parsing multiple extended properties flags."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        data = b"\x03\x00"  # Reliable Write and Writable Auxiliaries enabled

        result = ext_props.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CharacteristicExtendedPropertiesData)
        assert result.value.reliable_write is True
        assert result.value.writable_auxiliaries is True

    def test_parse_invalid_length(self) -> None:
        """Test parsing extended properties with invalid length."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        data = b"\x01"  # Too short

        result = ext_props.parse_value(data)
        assert not result.parse_success
        assert "Extended Properties data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic Extended Properties has correct UUID."""
        ext_props = CharacteristicExtendedPropertiesDescriptor()
        assert str(ext_props.uuid) == "00002900-0000-1000-8000-00805F9B34FB"
