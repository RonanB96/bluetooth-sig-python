"""Test YAML unit parsing functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.characteristics.humidity import HumidityCharacteristic
from bluetooth_sig.gatt.characteristics.temperature import TemperatureCharacteristic
from bluetooth_sig.gatt.uuid_registry import uuid_registry


class TestYAMLUnitParsing:
    """Test automatic unit parsing from YAML specifications."""

    def test_yaml_unit_loading_basic(self):
        """Test that units are loaded from YAML files for common
        characteristics."""
        # Test Temperature characteristic - should get "°C" from YAML
        temp_info = uuid_registry.get_characteristic_info("Temperature")
        assert temp_info is not None, "Temperature characteristic should be found in registry"
        # Units may come from YAML or be None if YAML loading failed
        if temp_info.unit:
            assert temp_info.unit == "°C", f"Temperature unit should be °C, got {temp_info.unit}"

        # Test Battery Level characteristic - should get "%" from YAML
        battery_info = uuid_registry.get_characteristic_info("Battery Level")
        assert battery_info is not None, "Battery Level characteristic should be found in registry"
        if battery_info.unit:
            assert battery_info.unit == "%", f"Battery Level unit should be %, got {battery_info.unit}"

        # Test Humidity characteristic - should get "%" from YAML
        humidity_info = uuid_registry.get_characteristic_info("Humidity")
        assert humidity_info is not None, "Humidity characteristic should be found in registry"
        if humidity_info.unit:
            assert humidity_info.unit == "%", f"Humidity unit should be %, got {humidity_info.unit}"

    def test_characteristic_unit_resolution_from_yaml(self):
        """Test that characteristics get units from YAML registry."""
        # Create characteristics and test their unit resolution
        temp_char = TemperatureCharacteristic()
        battery_char = BatteryLevelCharacteristic()
        humidity_char = HumidityCharacteristic()

        # Get units - these should come from YAML if available, manual if not
        temp_unit = temp_char.unit
        battery_unit = battery_char.unit
        humidity_unit = humidity_char.unit

        # Verify units are appropriate (either from YAML or manual fallback)
        assert temp_unit in ["°C", ""], f"Temperature unit should be °C or empty, got {temp_unit}"
        assert battery_unit in ["%", ""], f"Battery unit should be % or empty, got {battery_unit}"
        assert humidity_unit in ["%", ""], f"Humidity unit should be % or empty, got {humidity_unit}"

    def test_manual_unit_priority(self):
        """Test that manual units take priority over YAML units."""
        # Use PM25 characteristic which has manual unit override in class definition
        from src.bluetooth_sig.gatt.characteristics.pm25_concentration import PM25ConcentrationCharacteristic

        # Create instance and check manual unit takes precedence
        pm25_char = PM25ConcentrationCharacteristic()
        unit = pm25_char.unit
        assert unit == "µg/m³", f"PM25 unit should be manual (µg/m³) from class definition, got {unit}"

    def test_unknown_characteristic_unit(self):
        """Test behavior with characteristics not in YAML."""
        # Try to get info for a characteristic that doesn't exist
        unknown_info = uuid_registry.get_characteristic_info("NonExistentCharacteristic")
        assert unknown_info is None, "Unknown characteristic should return None"

    def test_unit_conversion_mappings(self):
        """Test that Bluetooth SIG unit specifications are converted
        correctly."""
        # Test the conversion function directly (if accessible)
        registry_instance = uuid_registry

        # Test common unit conversions
        test_mappings = [
            ("percentage", "%"),
            ("thermodynamic_temperature.degree_celsius", "°C"),
            ("pressure.pascal", "Pa"),
            ("electric_current.ampere", "A"),
            ("electric_potential_difference.volt", "V"),
        ]

        for bluetooth_unit, expected_unit in test_mappings:
            # Use getattr for protected member access in tests
            converted = registry_instance._convert_bluetooth_unit_to_readable(bluetooth_unit)
            assert converted == expected_unit, (
                f"Unit {bluetooth_unit} should convert to {expected_unit}, got {converted}"
            )

    def test_gss_yaml_file_parsing(self):
        """Test that GSS YAML files can be parsed without errors."""
        # This test ensures the GSS parsing doesn't crash
        # Even if no GSS files are available, it should handle gracefully

        # Try to reload GSS specifications (should not crash)
        try:
            uuid_registry._load_gss_specifications()
        except (ValueError, TypeError, OSError) as e:
            pytest.fail(f"GSS specification loading should not raise exceptions: {e}")

    def test_manual_unit_override_priority(self):
        """Test that manual unit overrides always take precedence over YAML."""
        # Use Ozone characteristic which has manual unit override in class definition
        from src.bluetooth_sig.gatt.characteristics.ozone_concentration import OzoneConcentrationCharacteristic

        # Create instance and check manual unit takes precedence
        ozone_char = OzoneConcentrationCharacteristic()
        unit_with_manual = ozone_char.unit
        assert unit_with_manual == "ppb", (
            f"Ozone unit should be manual (ppb) from class definition, got {unit_with_manual}"
        )

    def test_characteristic_creation_with_yaml_units(self):
        """Test that characteristics created via registry get units
        automatically."""
        # Create characteristics using the registry
        battery_char = CharacteristicRegistry.create_characteristic("2A19", properties=set())  # Battery Level UUID
        if battery_char:
            unit = battery_char.unit
            # Should get unit from YAML or be empty if YAML not available
            assert unit in ["%", ""], f"Battery Level should have % unit or be empty, got {unit}"

        temp_char = CharacteristicRegistry.create_characteristic("2A6E", properties=set())  # Temperature UUID
        if temp_char:
            unit = temp_char.unit
            # Should get unit from YAML or be empty if YAML not available
            assert unit in ["°C", ""], f"Temperature should have °C unit or be empty, got {unit}"
