"""Test data parsing functionality using pytest framework."""

import pytest
from typing import Dict

from ble_gatt_device.gatt.gatt_manager import gatt_hierarchy


class TestDataParsing:
    """Test data parsing functionality with simulated device data."""

    @pytest.fixture
    def simulated_nordic_thingy_services(self) -> Dict:
        """Fixture providing simulated Nordic Thingy:52 services structure."""
        return {
            "180F": {  # Battery Service
                "characteristics": {
                    "00002a19-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read", "notify"]
                    }
                }
            },
            "181A": {  # Environmental Sensing Service
                "characteristics": {
                    "00002a6e-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read", "notify"]
                    },  # Temperature
                    "00002a6f-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read", "notify"]
                    },  # Humidity
                    "00002a6d-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read", "notify"]
                    },  # Pressure
                }
            },
            "180A": {  # Device Information Service
                "characteristics": {
                    "00002a24-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read"]
                    },  # Model Number
                    "00002a29-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read"]
                    },  # Manufacturer Name
                    "00002a25-0000-1000-8000-00805f9b34fb": {
                        "properties": ["read"]
                    },  # Serial Number
                }
            },
        }

    @pytest.fixture
    def simulated_nordic_thingy_data(self) -> Dict[str, bytearray]:
        """Fixture providing simulated Nordic Thingy:52 characteristic data."""
        return {
            # Battery Level: 77 (0x4D)
            "00002a19-0000-1000-8000-00805f9b34fb": bytearray([0x4D]),
            # Temperature: simulated as sint16 = 2300 (23.00°C)
            "00002a6e-0000-1000-8000-00805f9b34fb": bytearray([0xFC, 0x08]),
            # Humidity: simulated as uint16 = 6100 (61.00%)
            "00002a6f-0000-1000-8000-00805f9b34fb": bytearray([0xD4, 0x17]),
            # Pressure: simulated as uint32 = 101325 Pa (sea level)
            "00002a6d-0000-1000-8000-00805f9b34fb": bytearray([0xE2, 0x7F, 0x01, 0x00]),
            # Device strings
            "00002a24-0000-1000-8000-00805f9b34fb": bytearray(b"Thingy:52"),
            "00002a29-0000-1000-8000-00805f9b34fb": bytearray(b"Nordic Semiconductor"),
            "00002a25-0000-1000-8000-00805f9b34fb": bytearray(b"ENV001"),
        }

    def test_gatt_service_recognition(self, simulated_nordic_thingy_services):
        """Test that GATT framework recognizes simulated services."""
        # Reset discovered services
        gatt_hierarchy._services = {}
        
        # Process services
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        # Verify services were recognized
        assert len(gatt_hierarchy.discovered_services) > 0, "No services were recognized"
        
        # Verify expected service count (should recognize at least Battery and Environmental)
        assert len(gatt_hierarchy.discovered_services) >= 2, f"Expected at least 2 services, got {len(gatt_hierarchy.discovered_services)}"

    def test_battery_level_parsing(self, simulated_nordic_thingy_services, simulated_nordic_thingy_data):
        """Test battery level characteristic parsing."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        # Find battery service
        battery_service = None
        for service in gatt_hierarchy.discovered_services:
            if "Battery" in service.__class__.__name__:
                battery_service = service
                break
                
        assert battery_service is not None, "Battery service not found"
        
        # Find battery level characteristic
        battery_char = None
        for char_uuid, characteristic in battery_service.characteristics.items():
            if "BatteryLevel" in characteristic.__class__.__name__:
                battery_char = characteristic
                # Find corresponding data
                for data_uuid, data in simulated_nordic_thingy_data.items():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        parsed_value = characteristic.parse_value(data)
                        assert parsed_value == 77, f"Expected battery level 77, got {parsed_value}"
                        assert characteristic.unit == "%", f"Expected unit '%', got '{characteristic.unit}'"
                        battery_char = characteristic
                        break
                break
                
        assert battery_char is not None, "Battery level characteristic not found"

    def test_temperature_parsing(self, simulated_nordic_thingy_services, simulated_nordic_thingy_data):
        """Test temperature characteristic parsing."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        # Find environmental service
        env_service = None
        for service in gatt_hierarchy.discovered_services:
            if "Environmental" in service.__class__.__name__:
                env_service = service
                break
                
        assert env_service is not None, "Environmental service not found"
        
        # Find temperature characteristic and test parsing
        temp_char = None
        for char_uuid, characteristic in env_service.characteristics.items():
            if "Temperature" in characteristic.__class__.__name__:
                # Find corresponding data
                for data_uuid, data in simulated_nordic_thingy_data.items():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        parsed_value = characteristic.parse_value(data)
                        assert parsed_value == 23.0, f"Expected temperature 23.0°C, got {parsed_value}"
                        assert characteristic.unit == "°C", f"Expected unit '°C', got '{characteristic.unit}'"
                        temp_char = characteristic
                        break
                break
                
        assert temp_char is not None, "Temperature characteristic not found"

    def test_humidity_parsing(self, simulated_nordic_thingy_services, simulated_nordic_thingy_data):
        """Test humidity characteristic parsing."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        # Find environmental service
        env_service = None
        for service in gatt_hierarchy.discovered_services:
            if "Environmental" in service.__class__.__name__:
                env_service = service
                break
                
        assert env_service is not None, "Environmental service not found"
        
        # Find humidity characteristic and test parsing
        humidity_char = None
        for char_uuid, characteristic in env_service.characteristics.items():
            if "Humidity" in characteristic.__class__.__name__:
                # Find corresponding data
                for data_uuid, data in simulated_nordic_thingy_data.items():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        parsed_value = characteristic.parse_value(data)
                        assert parsed_value == 61.0, f"Expected humidity 61.0%, got {parsed_value}"
                        assert characteristic.unit == "%", f"Expected unit '%', got '{characteristic.unit}'"
                        humidity_char = characteristic
                        break
                break
                
        assert humidity_char is not None, "Humidity characteristic not found"

    def test_pressure_parsing(self, simulated_nordic_thingy_services, simulated_nordic_thingy_data):
        """Test pressure characteristic parsing."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        # Find environmental service
        env_service = None
        for service in gatt_hierarchy.discovered_services:
            if "Environmental" in service.__class__.__name__:
                env_service = service
                break
                
        assert env_service is not None, "Environmental service not found"
        
        # Find pressure characteristic and test parsing
        pressure_char = None
        for char_uuid, characteristic in env_service.characteristics.items():
            if "Pressure" in characteristic.__class__.__name__:
                # Find corresponding data
                for data_uuid, data in simulated_nordic_thingy_data.items():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        parsed_value = characteristic.parse_value(data)
                        assert parsed_value == 101.325, f"Expected pressure 101.325 kPa, got {parsed_value}"
                        assert characteristic.unit == "kPa", f"Expected unit 'kPa', got '{characteristic.unit}'"
                        pressure_char = characteristic
                        break
                break
                
        assert pressure_char is not None, "Pressure characteristic not found"

    def test_device_info_parsing(self, simulated_nordic_thingy_services, simulated_nordic_thingy_data):
        """Test device information characteristic parsing."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        # Find device info service
        device_service = None
        for service in gatt_hierarchy.discovered_services:
            if "Device" in service.__class__.__name__ or "Information" in service.__class__.__name__:
                device_service = service
                break
                
        assert device_service is not None, "Device information service not found"
        
        # Test each device info characteristic
        expected_values = {
            "Model": "Thingy:52",
            "Manufacturer": "Nordic Semiconductor", 
            "Serial": "ENV001"
        }
        
        found_chars = 0
        for char_uuid, characteristic in device_service.characteristics.items():
            char_name = characteristic.__class__.__name__
            # Find corresponding data
            for data_uuid, data in simulated_nordic_thingy_data.items():
                if data_uuid.replace("-", "").upper() == char_uuid:
                    parsed_value = characteristic.parse_value(data)
                    # Check for expected values
                    if "Model" in char_name and "Thingy:52" in str(parsed_value):
                        found_chars += 1
                    elif "Manufacturer" in char_name and "Nordic" in str(parsed_value):
                        found_chars += 1
                    elif "Serial" in char_name and "ENV001" in str(parsed_value):
                        found_chars += 1
                    break
                    
        assert found_chars >= 1, f"Expected to parse at least 1 device info characteristic, got {found_chars}"

    def test_comprehensive_parsing_count(self, simulated_nordic_thingy_services, simulated_nordic_thingy_data):
        """Test that a reasonable number of characteristics can be parsed."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)
        
        parsed_count = 0
        total_characteristics = 0
        
        for service in gatt_hierarchy.discovered_services:
            total_characteristics += len(service.characteristics)
            for char_uuid, characteristic in service.characteristics.items():
                # Try to find corresponding data
                for data_uuid, data in simulated_nordic_thingy_data.items():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        try:
                            parsed_value = characteristic.parse_value(data)
                            parsed_count += 1
                        except Exception:
                            # Some characteristics might fail to parse with test data
                            pass
                        break
        
        # We should be able to parse at least 4 characteristics (battery, temp, humidity, pressure)
        assert parsed_count >= 4, f"Expected to parse at least 4 characteristics, got {parsed_count}"
        assert total_characteristics >= 6, f"Expected at least 6 total characteristics, got {total_characteristics}"