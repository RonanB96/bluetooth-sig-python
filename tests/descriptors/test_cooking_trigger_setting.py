"""Tests for Cooking Trigger Setting descriptor."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics.cooking_sensor_common import CookingSensorValue
from bluetooth_sig.gatt.descriptors.cooking_trigger_setting import (  # type: ignore[import-untyped]
    CookingTriggerSettingData,
    CookingTriggerSettingDescriptor,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class TestCookingTriggerSettingDescriptor:
    def test_parse_valid_data(self) -> None:
        sensor_uuid = BluetoothUUID(0x2C2E)
        descriptor = CookingTriggerSettingDescriptor(sensor_uuid=sensor_uuid)
        result = descriptor.parse_value(b"\x0a\x00\xc8\x00")
        assert result.parse_success is True
        assert isinstance(result.value, CookingTriggerSettingData)
        assert result.value.interval_100ms == 10
        assert result.value.delta == CookingSensorValue(sensor_uuid=sensor_uuid, value=20.0)

    def test_parse_invalid_length(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        result = descriptor.parse_value(b"\x78")
        assert result.parse_success is False
        assert "needs at least 2 bytes, got 1" in result.error_message

    def test_parse_without_sensor_uuid_fails(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        result = descriptor.parse_value(b"\x0a\x00\xc8\x00")
        assert result.parse_success is False
        assert "Cooking Sensor Info UUID is required" in result.error_message

    def test_parse_delta_length_mismatch_fails(self) -> None:
        descriptor = CookingTriggerSettingDescriptor(sensor_uuid=BluetoothUUID(0x2C2E))
        result = descriptor.parse_value(b"\x0a\x00\xc8")
        assert result.parse_success is False
        assert "must be 2 octets" in result.error_message

    def test_descriptor_is_writable(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        assert descriptor.is_writable() is True

    def test_uuid_resolution(self) -> None:
        descriptor = CookingTriggerSettingDescriptor()
        assert str(descriptor.uuid) == "00002917-0000-1000-8000-00805F9B34FB"
