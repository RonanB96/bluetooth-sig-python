"""Tests for IMD Trigger Setting descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import IMDTriggerSettingDescriptor
from bluetooth_sig.gatt.descriptors.imd_trigger_setting import IMDTriggerSettingData


class TestIMDTriggerSettingDescriptor:
    """Test IMD Trigger Setting descriptor functionality."""

    def test_parse_imd_trigger_setting(self) -> None:
        """Test parsing IMD trigger setting."""
        imd = IMDTriggerSettingDescriptor()
        # Trigger setting: 0x0001
        data = b"\x01\x00"

        result = imd.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, IMDTriggerSettingData)
        assert result.value.trigger_setting == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing IMD trigger setting with invalid length."""
        imd = IMDTriggerSettingDescriptor()
        data = b"\x01\x00\x00"  # Too long (3 bytes instead of 2)

        result = imd.parse_value(data)
        assert result.parse_success is False
        assert "IMD Trigger Setting data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that IMD Trigger Setting has correct UUID."""
        imd = IMDTriggerSettingDescriptor()
        assert str(imd.uuid) == "00002915-0000-1000-8000-00805F9B34FB"
