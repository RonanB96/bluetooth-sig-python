"""Test Home Assistant translation layer architecture."""

import pytest

from ble_gatt_device.gatt.ha_translation import GATTSensorTranslator
from ble_gatt_device.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from ble_gatt_device.gatt.characteristics.temperature import TemperatureCharacteristic
from ble_gatt_device.gatt.characteristics.illuminance import IlluminanceCharacteristic


class TestHATranslationLayer:
    """Test the Home Assistant translation layer architecture."""

    def test_gatt_to_ha_translation_battery(self):
        """Test translation of battery level characteristic to HA format."""
        # Create GATT characteristic (pure Bluetooth layer)
        battery_char = BatteryLevelCharacteristic(uuid="2A19", properties=set())
        raw_data = bytearray([75])  # 75% battery
        
        # Translate using translation layer
        ha_data = GATTSensorTranslator.translate_to_ha_sensor(battery_char, raw_data)
        
        # Verify HA-compatible format
        assert ha_data["value"] == 75, "Battery level should be parsed correctly"
        assert ha_data["unit_of_measurement"] == "%", "Unit should be percentage"
        assert ha_data["device_class"] == "battery", "Device class should be battery"
        assert ha_data["state_class"] == "measurement", "State class should be measurement"
        assert "2A19" in ha_data["unique_id"], "Unique ID should contain UUID"
        assert ha_data["name"] == "Battery Level", "Name should match characteristic name"

    def test_gatt_to_ha_translation_temperature(self):
        """Test translation of temperature characteristic to HA format.""" 
        # Create GATT characteristic (pure Bluetooth layer)
        temp_char = TemperatureCharacteristic(uuid="2A6E", properties=set())
        raw_data = bytearray([0xFC, 0x08])  # 2300 = 23.00°C
        
        # Translate using translation layer
        ha_data = GATTSensorTranslator.translate_to_ha_sensor(temp_char, raw_data)
        
        # Verify HA-compatible format
        assert ha_data["value"] == 23.0, "Temperature should be parsed correctly"
        assert ha_data["unit_of_measurement"] == "°C", "Unit should be Celsius"
        assert ha_data["device_class"] == "temperature", "Device class should be temperature"
        assert ha_data["state_class"] == "measurement", "State class should be measurement"

    def test_gatt_to_ha_translation_illuminance(self):
        """Test translation of illuminance characteristic to HA format."""
        # Create GATT characteristic (pure Bluetooth layer)
        illum_char = IlluminanceCharacteristic(uuid="2AFB", properties=set())
        raw_data = bytearray([0x10, 0x27, 0x00])  # 10000 = 100.00 lux
        
        # Translate using translation layer
        ha_data = GATTSensorTranslator.translate_to_ha_sensor(illum_char, raw_data)
        
        # Verify HA-compatible format
        assert ha_data["value"] == 100.0, "Illuminance should be parsed correctly"
        assert ha_data["unit_of_measurement"] == "lx", "Unit should be lux"
        assert ha_data["device_class"] == "illuminance", "Device class should be illuminance"
        assert ha_data["state_class"] == "measurement", "State class should be measurement"

    def test_sensor_configuration_generation(self):
        """Test generation of HA sensor configuration."""
        battery_char = BatteryLevelCharacteristic(uuid="2A19", properties=set())
        
        config = GATTSensorTranslator.get_sensor_configuration(battery_char)
        
        assert config["name"] == "Battery Level", "Name should match characteristic"
        assert config["device_class"] == "battery", "Device class should be battery"
        assert config["state_class"] == "measurement", "State class should be measurement"
        assert config["unit_of_measurement"] == "%", "Unit should be percentage"
        assert "mdi:battery" in config["icon"], "Icon should be battery-related"
        assert "2A19" in config["unique_id"], "Unique ID should contain UUID"

    def test_icon_mapping(self):
        """Test that appropriate icons are assigned to device classes."""
        # Test a few key device classes
        assert "thermometer" in GATTSensorTranslator._get_icon_for_device_class("temperature")
        assert "battery" in GATTSensorTranslator._get_icon_for_device_class("battery")
        assert "water-percent" in GATTSensorTranslator._get_icon_for_device_class("humidity")
        assert "brightness" in GATTSensorTranslator._get_icon_for_device_class("illuminance")
        assert "bluetooth" in GATTSensorTranslator._get_icon_for_device_class("unknown")

    def test_batch_translation(self):
        """Test batch translation of multiple characteristics."""
        # Create multiple GATT characteristics
        battery_char = BatteryLevelCharacteristic(uuid="2A19", properties=set())
        temp_char = TemperatureCharacteristic(uuid="2A6E", properties=set())
        
        characteristics = {
            "2A19": battery_char,
            "2A6E": temp_char
        }
        
        characteristic_data = {
            "2A19": bytearray([80]),  # 80% battery
            "2A6E": bytearray([0x84, 0x07])  # 1924 = 19.24°C
        }
        
        # Batch translate
        translated = GATTSensorTranslator.batch_translate_characteristics(
            characteristics, characteristic_data
        )
        
        # Verify both characteristics translated
        assert len(translated) == 2, "Should translate both characteristics"
        assert translated["2A19"]["value"] == 80, "Battery should be 80%"
        assert abs(translated["2A6E"]["value"] - 19.24) < 0.01, "Temperature should be approximately 19.24°C"

    def test_error_handling_in_translation(self):
        """Test that translation layer handles parsing errors gracefully."""
        battery_char = BatteryLevelCharacteristic(uuid="2A19", properties=set())
        invalid_data = bytearray([])  # Empty data should cause parse error
        
        ha_data = GATTSensorTranslator.translate_to_ha_sensor(battery_char, invalid_data)
        
        # Should return error information instead of crashing
        assert ha_data["value"] is None, "Value should be None on error"
        assert "error" in ha_data, "Should include error message"
        assert ha_data["characteristic_uuid"] == "2A19", "Should still include UUID"

    def test_architecture_separation_validation(self):
        """Test that translation layer properly separates concerns."""
        # This test validates the architecture:
        # 1. GATT characteristics contain only Bluetooth logic + metadata
        # 2. Translation layer calls GATT methods but doesn't import HA
        # 3. HA integration would call translation layer
        
        battery_char = BatteryLevelCharacteristic(uuid="2A19", properties=set())
        
        # GATT layer provides metadata properties (no HA imports)
        assert hasattr(battery_char, 'device_class'), "GATT should provide HA metadata"
        assert hasattr(battery_char, 'state_class'), "GATT should provide HA metadata"
        assert hasattr(battery_char, 'unit'), "GATT should provide unit metadata"
        assert hasattr(battery_char, 'parse_value'), "GATT should provide parsing logic"
        
        # Translation layer uses GATT metadata without HA imports
        raw_data = bytearray([50])
        ha_data = GATTSensorTranslator.translate_to_ha_sensor(battery_char, raw_data)
        
        # Verify translation layer produces HA-compatible data
        required_ha_fields = ["value", "unit_of_measurement", "device_class", "state_class", "name", "unique_id"]
        for field in required_ha_fields:
            assert field in ha_data, f"HA data should include {field}"
            
        # Verify no direct HA imports in translation module
        import inspect
        translation_source = inspect.getsource(GATTSensorTranslator)
        assert "from homeassistant" not in translation_source, "Translation layer should not import HA directly"
        assert "import homeassistant" not in translation_source, "Translation layer should not import HA directly"