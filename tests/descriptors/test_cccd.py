"""Tests for CCCD (Client Characteristic Configuration Descriptor) functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CCCDDescriptor
from bluetooth_sig.gatt.descriptors.cccd import CCCDData


class TestCCCDDescriptor:
    """Test CCCD descriptor functionality."""

    def test_parse_enable_notifications(self) -> None:
        """Test parsing CCCD value with notifications enabled."""
        cccd = CCCDDescriptor()
        data = b"\x01\x00"  # Notifications enabled

        result = cccd.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is True
        assert result.value.indications_enabled is False

    def test_parse_enable_indications(self) -> None:
        """Test parsing CCCD value with indications enabled."""
        cccd = CCCDDescriptor()
        data = b"\x02\x00"  # Indications enabled

        result = cccd.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is False
        assert result.value.indications_enabled is True

    def test_parse_enable_both(self) -> None:
        """Test parsing CCCD value with both notifications and indications enabled."""
        cccd = CCCDDescriptor()
        data = b"\x03\x00"  # Both enabled

        result = cccd.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is True
        assert result.value.indications_enabled is True

    def test_parse_disable_all(self) -> None:
        """Test parsing CCCD value with all disabled."""
        cccd = CCCDDescriptor()
        data = b"\x00\x00"  # All disabled

        result = cccd.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, CCCDData)
        assert result.value.notifications_enabled is False
        assert result.value.indications_enabled is False

    def test_parse_invalid_length(self) -> None:
        """Test parsing CCCD value with invalid length."""
        cccd = CCCDDescriptor()
        data = b"\x01"  # Too short

        result = cccd.parse_value(data)
        assert result.parse_success is False
        assert "need 2 bytes, got 1" in result.error_message

    def test_create_enable_values(self) -> None:
        """Test creating CCCD enable values."""
        assert CCCDDescriptor.create_enable_notifications_value() == b"\x01\x00"
        assert CCCDDescriptor.create_enable_indications_value() == b"\x02\x00"
        assert CCCDDescriptor.create_enable_both_value() == b"\x03\x00"
        assert CCCDDescriptor.create_disable_value() == b"\x00\x00"

    def test_uuid_resolution(self) -> None:
        """Test that CCCD has correct UUID."""
        cccd = CCCDDescriptor()
        assert str(cccd.uuid) == "00002902-0000-1000-8000-00805F9B34FB"
