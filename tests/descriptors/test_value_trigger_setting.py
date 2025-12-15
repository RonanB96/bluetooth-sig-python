"""Tests for Value Trigger Setting descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ValueTriggerSettingDescriptor
from bluetooth_sig.gatt.descriptors.value_trigger_setting import ValueTriggerSettingData


class TestValueTriggerSettingDescriptor:
    """Test Value Trigger Setting descriptor functionality."""

    def test_parse_value_trigger_setting(self) -> None:
        """Test parsing value trigger setting."""
        vts = ValueTriggerSettingDescriptor()
        # Condition: 0x01 (less than), Value: 0x0A
        data = b"\x01\x0a"

        result = vts.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ValueTriggerSettingData)
        assert result.value.condition == 0x01
        assert result.value.value == 0x0A

    def test_parse_invalid_length(self) -> None:
        """Test parsing value trigger setting with invalid length."""
        vts = ValueTriggerSettingDescriptor()
        data = b"\x01"  # Too short (1 byte, need at least 2)

        result = vts.parse_value(data)
        assert not result.parse_success
        assert "Value Trigger Setting data must be at least 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Value Trigger Setting has correct UUID."""
        vts = ValueTriggerSettingDescriptor()
        assert str(vts.uuid) == "0000290A-0000-1000-8000-00805F9B34FB"
