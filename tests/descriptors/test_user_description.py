"""Tests for Characteristic User Description descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CharacteristicUserDescriptionDescriptor
from bluetooth_sig.gatt.descriptors.characteristic_user_description import CharacteristicUserDescriptionData


class TestCharacteristicUserDescriptionDescriptor:
    """Test Characteristic User Description descriptor functionality."""

    def test_parse_valid_description(self) -> None:
        """Test parsing valid UTF-8 description."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b"Hello World"

        result = desc.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CharacteristicUserDescriptionData)
        assert result.value.description == "Hello World"

    def test_parse_empty_description(self) -> None:
        """Test parsing empty description."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b""

        result = desc.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CharacteristicUserDescriptionData)
        assert result.value.description == ""

    def test_parse_unicode_description(self) -> None:
        """Test parsing Unicode description."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = "温度传感器".encode()

        result = desc.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CharacteristicUserDescriptionData)
        assert result.value.description == "温度传感器"

    def test_parse_invalid_utf8(self) -> None:
        """Test parsing invalid UTF-8 data."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b"\xff\xfe\xfd"  # Invalid UTF-8

        result = desc.parse_value(data)
        assert result.parse_success is False
        assert "Invalid UTF-8 data" in result.error_message

    def test_get_description_helper(self) -> None:
        """Test get_description helper method."""
        desc = CharacteristicUserDescriptionDescriptor()
        data = b"Battery Level"

        assert desc.get_description(data) == "Battery Level"

    def test_uuid_resolution(self) -> None:
        """Test that Characteristic User Description has correct UUID."""
        desc = CharacteristicUserDescriptionDescriptor()
        assert str(desc.uuid) == "00002901-0000-1000-8000-00805F9B34FB"
