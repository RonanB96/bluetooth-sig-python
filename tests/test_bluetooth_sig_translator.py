"""Test Bluetooth SIG Translator functionality."""

from bluetooth_sig import BluetoothSIGTranslator


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
        assert hasattr(
            translator, "parse_characteristic"
        ), "Translator should have parse_characteristic method"
        assert hasattr(
            translator, "get_characteristic_info"
        ), "Translator should have get_characteristic_info method"
        assert hasattr(
            translator, "get_service_info"
        ), "Translator should have get_service_info method"
        assert hasattr(
            translator, "list_supported_characteristics"
        ), "Translator should have list_supported_characteristics method"
        assert hasattr(
            translator, "list_supported_services"
        ), "Translator should have list_supported_services method"

        # Test that methods are callable
        assert callable(
            translator.parse_characteristic
        ), "parse_characteristic should be callable"
        assert callable(
            translator.get_characteristic_info
        ), "get_characteristic_info should be callable"
        assert callable(
            translator.get_service_info
        ), "get_service_info should be callable"
        assert callable(
            translator.list_supported_characteristics
        ), "list_supported_characteristics should be callable"
        assert callable(
            translator.list_supported_services
        ), "list_supported_services should be callable"

    def test_parse_characteristic_fallback(self):
        """Test characteristic parsing returns raw data as fallback."""
        translator = BluetoothSIGTranslator()

        # Test with arbitrary UUID and data - should return raw data when no parser available
        raw_data = b"\x64"  # 100 in binary
        result = translator.parse_characteristic("unknown-uuid", raw_data)

        # Should return raw data when no parser found
        assert result == raw_data

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
            assert result == 100

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
        assert result == 100  # Should parse battery level characteristic (0x64 = 100%)

    def test_no_connection_methods(self):
        """Test that translator has no connection-related methods."""
        translator = BluetoothSIGTranslator()

        # Ensure no connection methods exist
        assert not hasattr(
            translator, "connect"
        ), "Translator should not have connect method"
        assert not hasattr(
            translator, "disconnect"
        ), "Translator should not have disconnect method"
        assert not hasattr(
            translator, "get_rssi"
        ), "Translator should not have get_rssi method"
        assert not hasattr(
            translator, "read_characteristics"
        ), "Translator should not have read_characteristics method"
        assert not hasattr(
            translator, "read_parsed_characteristics"
        ), "Translator should not have read_parsed_characteristics method"
        assert not hasattr(
            translator, "get_device_info"
        ), "Translator should not have get_device_info method"
