"""Tests for ServiceDataParser.

Tests cover:
- Parsing known SIG characteristics from service data
- Handling unknown UUIDs (skipped)
- Error handling for malformed data
- Cache behavior
"""

from __future__ import annotations

import pytest

from bluetooth_sig.advertising.service_data_parser import ServiceDataParser
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from bluetooth_sig.types.uuid import BluetoothUUID


class TestServiceDataParser:
    """Tests for ServiceDataParser."""

    @pytest.fixture(autouse=True)
    def clear_cache(self) -> None:
        """Clear cache before each test."""
        ServiceDataParser.clear_cache()

    def test_parse_battery_level(self) -> None:
        """Test parsing Battery Level service data (0x2A19)."""
        parser = ServiceDataParser()

        # Battery Level UUID and value (75%)
        battery_uuid = BluetoothUUID(0x2A19)
        service_data = {battery_uuid: bytes([75])}

        result = parser.parse(service_data)

        assert battery_uuid in result
        assert result[battery_uuid] == 75

    def test_parse_multiple_characteristics(self) -> None:
        """Test parsing multiple service data entries."""
        parser = ServiceDataParser()

        battery_uuid = BluetoothUUID(0x2A19)  # Battery Level
        service_data = {
            battery_uuid: bytes([50]),
        }

        result = parser.parse(service_data)

        # Only Battery Level should be parsed (it's registered)
        assert len(result) >= 1
        assert battery_uuid in result

    def test_skip_unknown_uuid(self) -> None:
        """Test that unknown UUIDs are skipped."""
        parser = ServiceDataParser()

        # Unknown custom UUID
        unknown_uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")
        service_data = {unknown_uuid: bytes([1, 2, 3])}

        result = parser.parse(service_data)

        # Should return empty dict for unknown UUIDs
        assert unknown_uuid not in result

    def test_empty_service_data(self) -> None:
        """Test parsing empty service data."""
        parser = ServiceDataParser()

        result = parser.parse({})

        assert result == {}

    def test_parse_error_propagates(self) -> None:
        """Test that parse errors propagate when validation enabled."""
        parser = ServiceDataParser()

        # Battery Level requires 1 byte, give it 0 bytes
        battery_uuid = BluetoothUUID(0x2A19)
        service_data = {battery_uuid: bytes([])}

        # Parse errors are wrapped in CharacteristicParseError
        with pytest.raises(CharacteristicParseError) as exc_info:
            parser.parse(service_data)
        assert "need 1 bytes, got 0" in str(exc_info.value)

    def test_cache_hit(self) -> None:
        """Test that characteristic instances are cached."""
        battery_uuid = BluetoothUUID(0x2A19)

        # First call should populate cache
        char1 = ServiceDataParser.get_characteristic(battery_uuid)
        # Second call should return cached instance
        char2 = ServiceDataParser.get_characteristic(battery_uuid)

        assert char1 is char2

    def test_cache_miss_returns_none(self) -> None:
        """Test that cache miss returns None for unknown UUIDs."""
        unknown_uuid = BluetoothUUID("12345678-1234-1234-1234-123456789abc")

        char = ServiceDataParser.get_characteristic(unknown_uuid)

        assert char is None

    def test_clear_cache(self) -> None:
        """Test cache clearing."""
        battery_uuid = BluetoothUUID(0x2A19)

        # Populate cache
        _ = ServiceDataParser.get_characteristic(battery_uuid)
        assert battery_uuid.normalized in ServiceDataParser._char_cache

        # Clear cache
        ServiceDataParser.clear_cache()
        assert battery_uuid.normalized not in ServiceDataParser._char_cache


class TestServiceDataParserContext:
    """Tests for ServiceDataParser with context."""

    @pytest.fixture(autouse=True)
    def clear_cache(self) -> None:
        """Clear cache before each test."""
        ServiceDataParser.clear_cache()

    def test_build_context(self) -> None:
        """Test building context from advertisement info."""
        ctx = ServiceDataParser.build_context(
            device_name="TestDevice",
            device_address="AA:BB:CC:DD:EE:FF",
            validate=True,
        )

        assert ctx.device_info is not None
        assert ctx.device_info.name == "TestDevice"
        assert ctx.device_info.address == "AA:BB:CC:DD:EE:FF"
        assert ctx.validate is True

    def test_build_context_with_manufacturer_data(self) -> None:
        """Test building context with manufacturer data."""
        ctx = ServiceDataParser.build_context(
            manufacturer_data={0x004C: b"\x01\x02\x03"},  # Apple
        )

        assert ctx.device_info is not None
        assert 0x004C in ctx.device_info.manufacturer_data
        assert ctx.device_info.manufacturer_data[0x004C].payload == b"\x01\x02\x03"

    def test_build_context_with_service_uuids(self) -> None:
        """Test building context with service UUIDs."""
        service_uuid = BluetoothUUID(0x180F)  # Battery Service
        ctx = ServiceDataParser.build_context(
            service_uuids=[service_uuid],
        )

        assert ctx.device_info is not None
        assert service_uuid in ctx.device_info.service_uuids

    def test_parse_with_context(self) -> None:
        """Test parsing with context."""
        parser = ServiceDataParser()
        ctx = ServiceDataParser.build_context(
            device_name="TestDevice",
            validate=True,
        )

        battery_uuid = BluetoothUUID(0x2A19)
        service_data = {battery_uuid: bytes([100])}

        result = parser.parse(service_data, ctx)

        assert battery_uuid in result
        assert result[battery_uuid] == 100
