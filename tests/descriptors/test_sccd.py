"""Tests for Server Characteristic Configuration descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ServerCharacteristicConfigurationDescriptor
from bluetooth_sig.gatt.descriptors.server_characteristic_configuration import SCCDData


class TestServerCharacteristicConfigurationDescriptor:
    """Test Server Characteristic Configuration descriptor functionality."""

    def test_parse_sccd_value(self) -> None:
        """Test parsing SCCD value."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        data = b"\x01\x00"  # Broadcasts enabled

        result = sccd.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, SCCDData)
        assert result.value.broadcasts_enabled is True

    def test_parse_invalid_length(self) -> None:
        """Test parsing SCCD with invalid length."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        data = b"\x01"  # Too short

        result = sccd.parse_value(data)
        assert result.parse_success is False
        assert "SCCD data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that SCCD has correct UUID."""
        sccd = ServerCharacteristicConfigurationDescriptor()
        assert str(sccd.uuid) == "00002903-0000-1000-8000-00805F9B34FB"
