"""Tests for Time Trigger Setting descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import TimeTriggerSettingDescriptor
from bluetooth_sig.gatt.descriptors.time_trigger_setting import TimeTriggerSettingData


class TestTimeTriggerSettingDescriptor:
    """Test Time Trigger Setting descriptor functionality."""

    def test_parse_time_trigger_setting(self) -> None:
        """Test parsing time trigger setting."""
        tts = TimeTriggerSettingDescriptor()
        # Value: 0x00000A00 (2560 seconds)
        data = b"\x00\x0a\x00"

        result = tts.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, TimeTriggerSettingData)
        assert result.value.time_interval == 0x000A00

    def test_parse_invalid_length(self) -> None:
        """Test parsing time trigger setting with invalid length."""
        tts = TimeTriggerSettingDescriptor()
        data = b"\x00\x0a"  # Too short (2 bytes instead of 3)

        result = tts.parse_value(data)
        assert result.parse_success is False
        assert "need 4 bytes, got 3" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Time Trigger Setting has correct UUID."""
        tts = TimeTriggerSettingDescriptor()
        assert str(tts.uuid) == "0000290E-0000-1000-8000-00805F9B34FB"
