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
        assert result.parse_success
        assert isinstance(result.value, TimeTriggerSettingData)
        assert result.value.time_interval == 0x000A00

    def test_parse_invalid_length(self) -> None:
        """Test parsing time trigger setting with invalid length."""
        tts = TimeTriggerSettingDescriptor()
        data = b"\x00\x0a\x00\x00"  # Too long (4 bytes instead of 3)

        result = tts.parse_value(data)
        assert not result.parse_success
        assert "Time Trigger Setting data must be exactly 3 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Time Trigger Setting has correct UUID."""
        tts = TimeTriggerSettingDescriptor()
        assert str(tts.uuid) == "0000290E-0000-1000-8000-00805F9B34FB"
