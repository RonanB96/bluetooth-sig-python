"""Tests for Cooking Sensor Info descriptor."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors.cooking_sensor_info import (  # type: ignore[import-untyped]
    CookingSensorInfoData,
    CookingSensorInfoDescriptor,
    CookingSensorLocation,
    CookingSensorLocationType,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class TestCookingSensorInfoDescriptor:
    def test_parse_valid_data(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x2e\x2c\x0a\x05\x02\x05\x00\x03\x00")
        assert result.parse_success is True
        assert isinstance(result.value, CookingSensorInfoData)
        assert result.value.sensor_uuid == BluetoothUUID(0x2C2E)
        assert result.value.measurement_uncertainty == 10
        assert result.value.location == CookingSensorLocation(
            location_type=CookingSensorLocationType.PROBE_FOOD_CORE,
            distance_mm=5,
        )
        assert result.value.aggregate_offset == 3

    def test_parse_valid_handle_location_without_data(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x2e\x2c\x0a\x07\x00")
        assert result.parse_success is True
        assert isinstance(result.value, CookingSensorInfoData)
        assert result.value.location == CookingSensorLocation(location_type=CookingSensorLocationType.HANDLE)

    def test_parse_invalid_length(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x12")
        assert result.parse_success is False
        assert "needs at least 5 bytes, got 1" in result.error_message

    def test_parse_rfu_location_type_fails(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x2e\x2c\x0a\x09\x00")
        assert result.parse_success is False
        assert "location type is RFU" in result.error_message

    def test_positioned_location_requires_distance_data(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x2e\x2c\x0a\x05\x01\x05")
        assert result.parse_success is False
        assert "requires 2 bytes of location data" in result.error_message

    def test_handle_location_rejects_location_data(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x2e\x2c\x0a\x07\x01\x05")
        assert result.parse_success is False
        assert "does not include location data" in result.error_message

    def test_invalid_trailing_aggregate_offset_length_fails(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        result = descriptor.parse_value(b"\x2e\x2c\x0a\x07\x00\x01")
        assert result.parse_success is False
        assert "invalid trailing aggregate offset length" in result.error_message

    def test_uuid_resolution(self) -> None:
        descriptor = CookingSensorInfoDescriptor()
        assert str(descriptor.uuid) == "00002916-0000-1000-8000-00805F9B34FB"
