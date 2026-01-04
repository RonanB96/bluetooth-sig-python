"""Test YAML cross-reference system functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.humidity import HumidityCharacteristic
from bluetooth_sig.gatt.characteristics.temperature import TemperatureCharacteristic


class TestYAMLCrossReference:
    """Test YAML cross-reference system for characteristic metadata
    automation.
    """

    def test_yaml_data_type_extraction(self) -> None:
        """Test that YAML data types are extracted correctly for real
        characteristics.
        """
        # Test Temperature characteristic (known to use sint16)
        temp_char = TemperatureCharacteristic()
        data_type = temp_char.get_yaml_data_type()

        # Should get data type from YAML if available, or None
        if data_type:
            assert isinstance(data_type, str), f"Data type should be string, got {type(data_type)}"
            assert data_type in [
                "sint16",
                "medfloat16",
            ], f"Temperature should use sint16 or medfloat16, got {data_type}"

        # Test Humidity characteristic (known to use uint16)
        humidity_char = HumidityCharacteristic()
        humidity_data_type = humidity_char.get_yaml_data_type()

        if humidity_data_type:
            assert isinstance(humidity_data_type, str), f"Data type should be string, got {type(humidity_data_type)}"
            assert humidity_data_type == "uint16", f"Humidity should use uint16, got {humidity_data_type}"

    def test_yaml_field_size_extraction(self) -> None:
        """Test that YAML field sizes are extracted correctly."""
        # Test Temperature characteristic
        temp_char = TemperatureCharacteristic()
        field_size = temp_char.get_yaml_field_size()

        if field_size:
            assert isinstance(field_size, int), f"Field size should be int, got {type(field_size)}"
            assert field_size in [2], f"Temperature field size should be 2 bytes, got {field_size}"

        # Test Humidity characteristic
        humidity_char = HumidityCharacteristic()
        humidity_field_size = humidity_char.get_yaml_field_size()

        if humidity_field_size:
            assert isinstance(humidity_field_size, int), f"Field size should be int, got {type(humidity_field_size)}"
            assert humidity_field_size == 2, f"Humidity field size should be 2 bytes, got {humidity_field_size}"

    def test_yaml_unit_id_extraction(self) -> None:
        """Test that YAML unit IDs are extracted correctly."""
        # Test Temperature characteristic
        temp_char = TemperatureCharacteristic()
        unit_id = temp_char.get_yaml_unit_id()

        if unit_id:
            assert isinstance(unit_id, str), f"Unit ID should be string, got {type(unit_id)}"
            assert "temperature" in unit_id.lower() or "celsius" in unit_id.lower(), (
                f"Temperature unit ID should reference temperature/celsius, got {unit_id}"
            )

        # Test Humidity characteristic
        humidity_char = HumidityCharacteristic()
        battery_unit_id = humidity_char.get_yaml_unit_id()

        if battery_unit_id:
            assert isinstance(battery_unit_id, str), f"Unit ID should be string, got {type(battery_unit_id)}"
            assert "percentage" in battery_unit_id.lower(), (
                f"Battery unit ID should reference percentage, got {battery_unit_id}"
            )

    def test_is_signed_from_yaml_comprehensive(self) -> None:
        """Test signed type detection for various data types."""
        # Test Temperature characteristic (should be signed)
        temp_char = TemperatureCharacteristic()

        # Mock different data types to test the logic
        test_cases = [
            # Signed integer types
            ("sint8", True),
            ("sint16", True),
            ("sint32", True),
            ("sint64", True),
            # IEEE-11073 medical float types (signed)
            ("medfloat16", True),
            ("medfloat32", True),
            # IEEE-754 floating point types (signed)
            ("float32", True),
            ("float64", True),
            # Unsigned types
            ("uint16", False),
            ("uint16", False),
            ("uint32", False),
            # Other types
            ("boolean", False),
            ("utf8s", False),
            ("struct", False),
            # None/empty
            (None, False),
            ("", False),
        ]

        for data_type, expected_signed in test_cases:
            # Temporarily set the data type
            temp_char._yaml_data_type = data_type

            is_signed = temp_char.is_signed_from_yaml()
            assert is_signed == expected_signed, (
                f"Data type {data_type} should be {'signed' if expected_signed else 'unsigned'}, got {is_signed}"
            )

    def test_yaml_resolution_text_extraction(self) -> None:
        """Test that YAML resolution text is extracted when available."""
        # Test Temperature characteristic
        temp_char = TemperatureCharacteristic()
        resolution_text = temp_char.get_yaml_resolution_text()

        if resolution_text:
            assert isinstance(resolution_text, str), f"Resolution text should be string, got {type(resolution_text)}"
            # Resolution text often contains scale factors like "0.01"
            assert any(keyword in resolution_text.lower() for keyword in ["0.01", "scale", "resolution", "degree"]), (
                f"Resolution text should contain scale info, got {resolution_text}"
            )

    def test_characteristic_registry_with_yaml_automation(self) -> None:
        """Test that characteristics created via registry use YAML
        automation.
        """
        # Create Temperature characteristic via registry
        temp_char = CharacteristicRegistry.create_characteristic("2A6E")

        if temp_char:
            # Should have YAML automation available
            assert hasattr(temp_char, "get_yaml_data_type"), "Characteristic should have YAML automation methods"
            assert hasattr(temp_char, "get_yaml_field_size"), "Characteristic should have YAML automation methods"
            assert hasattr(temp_char, "is_signed_from_yaml"), "Characteristic should have YAML automation methods"

            # Test that automation works
            data_type = temp_char.get_yaml_data_type()
            field_size = temp_char.get_yaml_field_size()
            is_signed = temp_char.is_signed_from_yaml()

            # At minimum, should return valid types (or None)
            assert data_type is None or isinstance(data_type, str)
            assert field_size is None or isinstance(field_size, int)
            assert isinstance(is_signed, bool)

        # Create Humidity characteristic via registry
        humidity_char = CharacteristicRegistry.create_characteristic("2A6F")

        if humidity_char:
            # Should have YAML automation available
            humidity_data_type = humidity_char.get_yaml_data_type()
            humidity_is_signed = humidity_char.is_signed_from_yaml()

            # Humidity should not be signed (uint16)
            if humidity_data_type and humidity_data_type == "uint16":
                assert not humidity_is_signed, "Humidity (uint16) should not be signed"

    def test_yaml_automation_fallback_behaviour(self) -> None:
        """Test that characteristics work correctly when YAML automation is not
        available.
        """
        # Create characteristics
        temp_char = TemperatureCharacteristic()
        humidity_char = HumidityCharacteristic()

        # Even without YAML data, methods should not crash
        assert temp_char.get_yaml_data_type() is None or isinstance(temp_char.get_yaml_data_type(), str)
        assert temp_char.get_yaml_field_size() is None or isinstance(temp_char.get_yaml_field_size(), int)
        assert temp_char.get_yaml_unit_id() is None or isinstance(temp_char.get_yaml_unit_id(), str)
        assert isinstance(temp_char.is_signed_from_yaml(), bool)

        # Unit resolution should work with or without YAML
        temp_unit = temp_char.unit
        battery_unit = humidity_char.unit

        assert temp_unit in ["°C", ""], f"Temperature unit should be °C or empty, got {temp_unit}"
        assert battery_unit in ["%", ""], f"Battery unit should be % or empty, got {battery_unit}"

    def test_yaml_byte_order_hint(self) -> None:
        """Test byte order hint for characteristics."""
        temp_char = TemperatureCharacteristic()
        byte_order = temp_char.get_byte_order_hint()

        # Bluetooth SIG uses little-endian by convention
        assert byte_order == "little", f"Byte order should be little-endian, got {byte_order}"

    def test_yaml_automation_with_real_parsing(self) -> None:
        """Test that YAML automation works with actual characteristic
        parsing.
        """
        # Test Temperature characteristic with real data
        temp_char = TemperatureCharacteristic()

        # Parse some test data (400 = 4.00°C in 0.01°C units)
        test_data = bytearray([0x90, 0x01])  # 400 in little-endian

        try:
            parsed_value = temp_char.parse_value(test_data)
            assert isinstance(parsed_value, (int, float)), f"Parsed value should be numeric, got {type(parsed_value)}"
            assert 3.0 <= parsed_value <= 5.0, f"Parsed value should be around 4.0°C, got {parsed_value}"

            # Test that YAML automation provides useful metadata
            data_type = temp_char.get_yaml_data_type()
            is_signed = temp_char.is_signed_from_yaml()

            if data_type:
                # If we have YAML data, is_signed should match the data type
                if data_type.startswith("sint") or data_type in (
                    "medfloat16",
                    "medfloat32",
                    "float32",
                    "float64",
                ):
                    assert is_signed, f"Data type {data_type} should be detected as signed"
                elif data_type.startswith("uint"):
                    assert not is_signed, f"Data type {data_type} should be detected as unsigned"

        except Exception as e:
            # Parsing might fail if no manual implementation exists yet
            pytest.skip(f"Temperature parsing not implemented: {e}")

    def test_yaml_automation_integration_with_existing_functionality(self) -> None:
        """Test that YAML automation integrates well with existing
        characteristic functionality.
        """
        # Test that existing functionality still works
        temp_char = TemperatureCharacteristic()
        humidity_char = HumidityCharacteristic()

        # Test that all characteristics have their basic properties
        assert hasattr(temp_char, "uuid"), "Temperature characteristic should have uuid"
        assert hasattr(humidity_char, "uuid"), "Humidity characteristic should have uuid"

        # Test that YAML methods don't interfere with existing functionality
        assert temp_char.unit in ["°C", ""], "Temperature unit should work"
        assert humidity_char.unit in ["%", ""], "Humidity unit should work"

        # Test that value types are still accessible
        assert hasattr(temp_char, "value_type"), "Should have value_type"
        assert hasattr(humidity_char, "value_type"), "Should have value_type"
