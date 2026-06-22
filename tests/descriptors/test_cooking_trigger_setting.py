"""Tests for Cooking Trigger Setting descriptor."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors.cooking_trigger_setting import (  # type: ignore[import-untyped]
    CookingTriggerSettingData,
    CookingTriggerSettingDescriptor,
)


class TestCookingTriggerSettingDescriptor:
    def test_parse_valid_data(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        result = descriptor.parse_value(b"\x78\x56")
        assert result.parse_success is True
        assert isinstance(result.value, CookingTriggerSettingData)
        assert result.value.trigger_setting == 0x5678

    def test_parse_invalid_length(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        result = descriptor.parse_value(b"\x78")
        assert result.parse_success is False
        assert "need 2 bytes, got 1" in result.error_message

    def test_uuid_resolution(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        assert str(descriptor.uuid) == "00002917-0000-1000-8000-00805F9B34FB"
