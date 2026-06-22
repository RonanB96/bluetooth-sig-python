"""Tests for Cooking Sensor Info descriptor."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors.cooking_sensor_info import (  # type: ignore[import-untyped]
    CookingSensorInfoData,
    CookingSensorInfoDescriptor,
)


class TestCookingSensorInfoDescriptor:
    def test_parse_valid_data(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x34\x12")
        assert result.parse_success is True
        assert isinstance(result.value, CookingSensorInfoData)
        assert result.value.sensor_info == 0x1234

    def test_parse_invalid_length(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x12")
        assert result.parse_success is False
        assert "need 2 bytes, got 1" in result.error_message

    def test_uuid_resolution(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        assert str(descriptor.uuid) == "00002916-0000-1000-8000-00805F9B34FB"
