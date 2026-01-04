"""Test Bluetooth SIG Translator functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types import ValidationResult
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName


class TestBluetoothSIGTranslator:
    """Test BluetoothSIGTranslator SIG standards functionality."""

    def test_translator_instantiation(self) -> None:
        """Test that BluetoothSIGTranslator can be instantiated correctly."""
        translator = BluetoothSIGTranslator()

        assert translator is not None
        assert str(translator) == "BluetoothSIGTranslator(pure SIG standards)"

    def test_translator_methods_exist(self) -> None:
        """Test that essential methods exist on BluetoothSIGTranslator."""
        translator = BluetoothSIGTranslator()

        # Test that core methods exist
        assert hasattr(translator, "parse_characteristic"), "Translator should have parse_characteristic method"
        assert hasattr(translator, "get_characteristic_info_by_uuid"), (
            "Translator should have get_characteristic_info_by_uuid method"
        )
        assert hasattr(translator, "get_service_info_by_uuid"), "Translator should have get_service_info_by_uuid method"
        assert hasattr(translator, "list_supported_characteristics"), (
            "Translator should have list_supported_characteristics method"
        )
        assert hasattr(translator, "list_supported_services"), "Translator should have list_supported_services method"

        # Test that methods are callable
        assert callable(translator.parse_characteristic), "parse_characteristic should be callable"
        assert callable(translator.get_characteristic_info_by_uuid), (
            "get_characteristic_info_by_uuid should be callable"
        )
        assert callable(translator.get_service_info_by_uuid), "get_service_info_by_uuid should be callable"
        assert callable(translator.list_supported_characteristics), "list_supported_characteristics should be callable"
        assert callable(translator.list_supported_services), "list_supported_services should be callable"

    def test_parse_characteristic_fallback(self) -> None:
        """Test characteristic parsing raises exception for unknown UUID."""
        translator = BluetoothSIGTranslator()

        # Test with arbitrary UUID and data - should raise exception
        # when no parser available
        raw_data = b"\x64"  # 100 in binary
        unknown_uuid = "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"

        # Should raise CharacteristicParseError for unknown UUID
        with pytest.raises(Exception):  # Could be CharacteristicParseError or similar
            translator.parse_characteristic(unknown_uuid, raw_data)

    def test_parse_characteristic_with_uuid_formats(self) -> None:
        """Test characteristic parsing with different UUID formats."""
        translator = BluetoothSIGTranslator()

        raw_data = b"\x64"

        # Test different UUID formats - should all work
        uuids = [
            "2A19",
            "00002A19-0000-1000-8000-00805F9B34FB",
            "00002a19-0000-1000-8000-00805f9b34fb",
        ]

        for uuid in uuids:
            result = translator.parse_characteristic(uuid, raw_data)
            # Should parse known battery level characteristic (0x64 = 100%)
            assert result == 100

    def test_get_characteristic_info_fallback(self) -> None:
        """Test get_characteristic_info returns None for unknown characteristics."""
        translator = BluetoothSIGTranslator()

        # Test with unknown UUID
        unknown_uuid = "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"
        result = translator.get_characteristic_info_by_uuid(unknown_uuid)
        assert result is None

    def test_get_service_info_fallback(self) -> None:
        """Test get_service_info returns None for unknown services."""
        translator = BluetoothSIGTranslator()

        # Test with unknown UUID
        unknown_uuid = "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"
        result = translator.get_service_info_by_uuid(unknown_uuid)
        assert result is None

    def test_list_supported_characteristics(self) -> None:
        """Test listing supported characteristics."""
        translator = BluetoothSIGTranslator()

        characteristics = translator.list_supported_characteristics()
        assert isinstance(characteristics, dict)

    def test_list_supported_services(self) -> None:
        """Test listing supported services."""
        translator = BluetoothSIGTranslator()

        services = translator.list_supported_services()
        assert isinstance(services, dict)

    def test_pure_sig_translation_pattern(self) -> None:
        """Test the pure SIG translation pattern from docs."""
        translator = BluetoothSIGTranslator()

        def parse_sensor_reading(char_uuid: str, raw_data: bytes) -> int:
            """Pure SIG standard translation - no connection dependencies."""
            return translator.parse_characteristic(char_uuid, raw_data)

        # Test the pattern works
        result = parse_sensor_reading("2A19", b"\x64")
        # Should parse battery level characteristic (0x64 = 100%)
        assert result == 100

    def test_no_connection_methods(self) -> None:
        """Test that translator has no connection-related methods."""
        translator = BluetoothSIGTranslator()

        # Ensure no connection methods exist
        assert not hasattr(translator, "connect"), "Translator should not have connect method"
        assert not hasattr(translator, "disconnect"), "Translator should not have disconnect method"
        assert not hasattr(translator, "get_rssi"), "Translator should not have get_rssi method"
        assert not hasattr(translator, "read_characteristics"), "Translator should not have read_characteristics method"
        assert not hasattr(translator, "read_parsed_characteristics"), (
            "Translator should not have read_parsed_characteristics method"
        )
        assert not hasattr(translator, "get_device_info"), "Translator should not have get_device_info method"

    def test_resolve_uuid_with_characteristic_name(self) -> None:
        """Test resolving characteristic name to full info."""
        translator = BluetoothSIGTranslator()

        # Test known characteristic
        result = translator.get_sig_info_by_name("Battery Level")
        assert result is not None, "Should find Battery Level characteristic"
        assert str(result.uuid) == "00002A19-0000-1000-8000-00805F9B34FB"
        assert result.name == "Battery Level"

        # Test unknown characteristic
        result = translator.get_sig_info_by_name("Unknown Characteristic")
        assert result is None

    def test_resolve_name_with_uuid(self) -> None:
        """Test resolving UUID to full SIG information."""
        translator = BluetoothSIGTranslator()

        # Test known UUID
        result = translator.get_sig_info_by_uuid("2A19")
        assert result is not None, "Should find info for 2A19"
        assert result.name == "Battery Level", f"Expected 'Battery Level', got {result.name}"
        assert str(result.uuid) == "00002A19-0000-1000-8000-00805F9B34FB"

        # Test unknown UUID
        result = translator.get_sig_info_by_uuid("FFFF")
        assert result is None

    def test_parse_characteristics_batch(self) -> None:
        """Test parsing multiple characteristics at once."""
        translator = BluetoothSIGTranslator()

        # Test batch parsing
        char_data = {
            "2A19": b"\x64",  # Battery Level: 100%
            "2A6E": bytes(bytearray([0x90, 0x01])),  # Temperature: 4.0°C
        }

        results = translator.parse_characteristics(char_data)

        assert len(results) == 2
        # Results are now parsed values directly
        assert results["2A19"] == 100  # Battery level parsed
        # Temperature should be parsed (400 * 0.01 = 4.0)
        assert isinstance(results["2A6E"], float)

    def test_get_characteristics_info_batch(self) -> None:
        """Test getting info for multiple characteristics."""
        translator = BluetoothSIGTranslator()

        uuids = ["2A19", "2A6E", "FFFF"]  # Known, known, unknown
        results = translator.get_characteristics_info_by_uuids(uuids)

        assert len(results) == 3
        assert results["2A19"] is not None  # Battery Level should be found
        assert results["2A6E"] is not None  # Temperature should be found
        assert results["FFFF"] is None  # Unknown should be None

    def test_validate_characteristic_data(self) -> None:
        """Test validating characteristic data format."""
        translator = BluetoothSIGTranslator()

        # Valid battery level data
        result = translator.validate_characteristic_data("2A19", b"\x64")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.actual_length == 1

        # Invalid data that would cause parsing issues
        result = translator.validate_characteristic_data("2A19", b"")
        assert isinstance(result, ValidationResult)
        assert result.actual_length == 0

    def test_get_service_characteristics(self) -> None:
        """Test getting characteristics for a service."""
        translator = BluetoothSIGTranslator()

        # Test with battery service
        chars = translator.get_service_characteristics("180F")
        # Result depends on whether service defines required characteristics
        assert isinstance(chars, list)

        # Test with unknown service
        chars = translator.get_service_characteristics("FFFF")
        assert chars == []

    def test_get_characteristic_uuid_by_name(self) -> None:
        """Test getting characteristic UUID from CharacteristicName enum."""
        translator = BluetoothSIGTranslator()

        # Test known characteristic - Battery Level
        uuid = translator.get_characteristic_uuid_by_name(CharacteristicName.BATTERY_LEVEL)
        assert uuid is not None, "Should find UUID for BATTERY_LEVEL"
        assert str(uuid) == "00002A19-0000-1000-8000-00805F9B34FB"

        # Test another known characteristic - Heart Rate Measurement
        uuid = translator.get_characteristic_uuid_by_name(CharacteristicName.HEART_RATE_MEASUREMENT)
        assert uuid is not None, "Should find UUID for HEART_RATE_MEASUREMENT"
        assert str(uuid) == "00002A37-0000-1000-8000-00805F9B34FB"

        # Test Temperature characteristic
        uuid = translator.get_characteristic_uuid_by_name(CharacteristicName.TEMPERATURE)
        assert uuid is not None, "Should find UUID for TEMPERATURE"
        assert str(uuid) == "00002A6E-0000-1000-8000-00805F9B34FB"

    def test_get_characteristic_info_by_name(self) -> None:
        """Test getting characteristic info from CharacteristicName enum."""
        translator = BluetoothSIGTranslator()

        # Test known characteristic - Battery Level
        info = translator.get_characteristic_info_by_name(CharacteristicName.BATTERY_LEVEL)
        assert info is not None, "Should find info for BATTERY_LEVEL"
        assert info.name == "Battery Level"
        assert str(info.uuid) == "00002A19-0000-1000-8000-00805F9B34FB"
        assert info.unit == "%"

        # Test Heart Rate Measurement
        info = translator.get_characteristic_info_by_name(CharacteristicName.HEART_RATE_MEASUREMENT)
        assert info is not None, "Should find info for HEART_RATE_MEASUREMENT"
        assert info.name == "Heart Rate Measurement"
        assert str(info.uuid) == "00002A37-0000-1000-8000-00805F9B34FB"

        # Test Temperature
        info = translator.get_characteristic_info_by_name(CharacteristicName.TEMPERATURE)
        assert info is not None, "Should find info for TEMPERATURE"
        assert info.name == "Temperature"
        assert str(info.uuid) == "00002A6E-0000-1000-8000-00805F9B34FB"

    def test_get_service_uuid_by_name(self) -> None:
        """Test getting service UUID from ServiceName enum."""
        translator = BluetoothSIGTranslator()

        # Test known service - Battery Service
        uuid = translator.get_service_uuid_by_name(ServiceName.BATTERY)
        assert uuid is not None, "Should find UUID for BATTERY"
        assert str(uuid) == "0000180F-0000-1000-8000-00805F9B34FB"

        # Test Heart Rate service
        uuid = translator.get_service_uuid_by_name(ServiceName.HEART_RATE)
        assert uuid is not None, "Should find UUID for HEART_RATE"
        assert str(uuid) == "0000180D-0000-1000-8000-00805F9B34FB"

        # Test Device Information service
        uuid = translator.get_service_uuid_by_name(ServiceName.DEVICE_INFORMATION)
        assert uuid is not None, "Should find UUID for DEVICE_INFORMATION"
        assert str(uuid) == "0000180A-0000-1000-8000-00805F9B34FB"

    def test_enum_based_workflow(self) -> None:
        """Test the complete workflow using enum-based lookups (as shown in docs)."""
        translator = BluetoothSIGTranslator()

        # Step 1: Get UUID from enum (what's documented in usage.md)
        found_uuid = translator.get_characteristic_uuid_by_name(CharacteristicName.BATTERY_LEVEL)
        assert found_uuid is not None, "Should find Battery Level UUID"

        # Step 2: Use that UUID to parse data
        simulated_data = bytearray([85])  # 85% battery
        result = translator.parse_characteristic(str(found_uuid), simulated_data)

        # Step 3: Verify the result
        assert result == 85

        # Test that multiple UUID formats work (as documented)
        formats = [
            str(found_uuid),  # Full 128-bit from enum lookup
            "0x2A19",  # Hex prefix
            "00002a19-0000-1000-8000-00805f9b34fb",  # Lowercase
            "00002A19-0000-1000-8000-00805F9B34FB",  # Uppercase
        ]

        for uuid_format in formats:
            result = translator.parse_characteristic(uuid_format, simulated_data)
            assert result == 85, f"Should parse with format: {uuid_format}"
