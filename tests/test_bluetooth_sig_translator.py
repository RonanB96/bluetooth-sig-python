"""Test Bluetooth SIG Translator functionality."""

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.core import CharacteristicData, ValidationResult


class TestBluetoothSIGTranslator:
    """Test BluetoothSIGTranslator SIG standards functionality."""

    def test_translator_instantiation(self):
        """Test that BluetoothSIGTranslator can be instantiated correctly."""
        translator = BluetoothSIGTranslator()

        assert translator is not None
        assert str(translator) == "BluetoothSIGTranslator(pure SIG standards)"

    def test_translator_methods_exist(self):
        """Test that essential methods exist on BluetoothSIGTranslator."""
        translator = BluetoothSIGTranslator()

        # Test that core methods exist
        assert hasattr(translator, "parse_characteristic"), (
            "Translator should have parse_characteristic method"
        )
        assert hasattr(translator, "get_characteristic_info"), (
            "Translator should have get_characteristic_info method"
        )
        assert hasattr(translator, "get_service_info"), (
            "Translator should have get_service_info method"
        )
        assert hasattr(translator, "list_supported_characteristics"), (
            "Translator should have list_supported_characteristics method"
        )
        assert hasattr(translator, "list_supported_services"), (
            "Translator should have list_supported_services method"
        )

        # Test that methods are callable
        assert callable(translator.parse_characteristic), (
            "parse_characteristic should be callable"
        )
        assert callable(translator.get_characteristic_info), (
            "get_characteristic_info should be callable"
        )
        assert callable(translator.get_service_info), (
            "get_service_info should be callable"
        )
        assert callable(translator.list_supported_characteristics), (
            "list_supported_characteristics should be callable"
        )
        assert callable(translator.list_supported_services), (
            "list_supported_services should be callable"
        )

    def test_parse_characteristic_fallback(self):
        """Test characteristic parsing returns fallback data."""
        translator = BluetoothSIGTranslator()

        # Test with arbitrary UUID and data - should return fallback
        # when no parser available
        raw_data = b"\x64"  # 100 in binary
        result = translator.parse_characteristic("unknown-uuid", raw_data)

        # Should return CharacteristicData with fallback info when no parser found
        assert isinstance(result, CharacteristicData)
        assert result.uuid == "unknown-uuid"
        assert result.name == "Unknown"
        assert result.value == raw_data
        assert result.parse_success is False

    def test_parse_characteristic_with_uuid_formats(self):
        """Test characteristic parsing with different UUID formats."""
        translator = BluetoothSIGTranslator()

        raw_data = b"\x64"

        # Test different UUID formats - should all work
        uuids = [
            "2A19",  # Short form
            "00002A19-0000-1000-8000-00805F9B34FB",  # Full form with dashes
            "00002a19-0000-1000-8000-00805f9b34fb",  # Lowercase
        ]

        for uuid in uuids:
            result = translator.parse_characteristic(uuid, raw_data)
            # Should parse known battery level characteristic (0x64 = 100%)
            assert isinstance(result, CharacteristicData)
            assert result.value == 100
            assert result.parse_success is True

    def test_get_characteristic_info_fallback(self):
        """Test get_characteristic_info returns None for unknown characteristics."""
        translator = BluetoothSIGTranslator()

        # Test with unknown UUID
        result = translator.get_characteristic_info("unknown-uuid")
        assert result is None

    def test_get_service_info_fallback(self):
        """Test get_service_info returns None for unknown services."""
        translator = BluetoothSIGTranslator()

        # Test with unknown UUID
        result = translator.get_service_info("unknown-uuid")
        assert result is None

    def test_list_supported_characteristics(self):
        """Test listing supported characteristics."""
        translator = BluetoothSIGTranslator()

        characteristics = translator.list_supported_characteristics()
        assert isinstance(characteristics, dict)
        # Without YAML registry, may be empty but should be a dict

    def test_list_supported_services(self):
        """Test listing supported services."""
        translator = BluetoothSIGTranslator()

        services = translator.list_supported_services()
        assert isinstance(services, dict)
        # Without YAML registry, may be empty but should be a dict

    def test_pure_sig_translation_pattern(self):
        """Test the pure SIG translation pattern from docs."""
        translator = BluetoothSIGTranslator()

        def parse_sensor_reading(char_uuid: str, raw_data: bytes):
            """Pure SIG standard translation - no connection dependencies."""
            return translator.parse_characteristic(char_uuid, raw_data)

        # Test the pattern works
        result = parse_sensor_reading("2A19", b"\x64")
        assert isinstance(result, CharacteristicData)
        # Should parse battery level characteristic (0x64 = 100%)
        assert result.value == 100
        assert result.parse_success is True

    def test_no_connection_methods(self):
        """Test that translator has no connection-related methods."""
        translator = BluetoothSIGTranslator()

        # Ensure no connection methods exist
        assert not hasattr(translator, "connect"), (
            "Translator should not have connect method"
        )
        assert not hasattr(translator, "disconnect"), (
            "Translator should not have disconnect method"
        )
        assert not hasattr(translator, "get_rssi"), (
            "Translator should not have get_rssi method"
        )
        assert not hasattr(translator, "read_characteristics"), (
            "Translator should not have read_characteristics method"
        )
        assert not hasattr(translator, "read_parsed_characteristics"), (
            "Translator should not have read_parsed_characteristics method"
        )
        assert not hasattr(translator, "get_device_info"), (
            "Translator should not have get_device_info method"
        )

    def test_resolve_uuid_with_characteristic_name(self):
        """Test resolving characteristic name to full info."""
        translator = BluetoothSIGTranslator()

        # Test known characteristic
        result = translator.resolve_uuid("Battery Level")
        assert result is not None, "Should find Battery Level characteristic"
        assert result.uuid == "2A19", f"Expected 2A19, got {result.uuid}"
        assert result.name == "Battery Level"

        # Test unknown characteristic
        result = translator.resolve_uuid("Unknown Characteristic")
        assert result is None

    def test_resolve_name_with_uuid(self):
        """Test resolving UUID to full SIG information."""
        translator = BluetoothSIGTranslator()

        # Test known UUID
        result = translator.resolve_name("2A19")
        assert result is not None, "Should find info for 2A19"
        assert result.name == "Battery Level", (
            f"Expected 'Battery Level', got {result.name}"
        )
        assert result.uuid == "2A19"

        # Test unknown UUID
        result = translator.resolve_name("FFFF")
        assert result is None

    def test_parse_characteristics_batch(self):
        """Test parsing multiple characteristics at once."""
        translator = BluetoothSIGTranslator()

        # Test batch parsing
        char_data = {
            "2A19": b"\x64",  # Battery Level: 100%
            "2A6E": bytearray([0x90, 0x01]),  # Temperature: 4.0°C
        }

        results = translator.parse_characteristics(char_data)

        assert len(results) == 2
        # Results are now CharacteristicData objects
        assert isinstance(results["2A19"], CharacteristicData)
        assert results["2A19"].value == 100  # Battery level parsed
        assert isinstance(results["2A6E"], CharacteristicData)
        # Temperature should be parsed (400 * 0.01 = 4.0)
        assert isinstance(results["2A6E"].value, float)

    def test_get_characteristics_info_batch(self):
        """Test getting info for multiple characteristics."""
        translator = BluetoothSIGTranslator()

        uuids = ["2A19", "2A6E", "FFFF"]  # Known, known, unknown
        results = translator.get_characteristics_info(uuids)

        assert len(results) == 3
        assert results["2A19"] is not None  # Battery Level should be found
        assert results["2A6E"] is not None  # Temperature should be found
        assert results["FFFF"] is None  # Unknown should be None

    def test_validate_characteristic_data(self):
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

    def test_get_service_characteristics(self):
        """Test getting characteristics for a service."""
        translator = BluetoothSIGTranslator()

        # Test with battery service
        chars = translator.get_service_characteristics("180F")
        # Result depends on whether service defines required characteristics
        assert isinstance(chars, list)

        # Test with unknown service
        chars = translator.get_service_characteristics("FFFF")
        assert chars == []
