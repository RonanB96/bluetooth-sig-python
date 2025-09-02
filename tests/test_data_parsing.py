"""Test data parsing functionality using pytest framework."""

import pytest

from ble_gatt_device.gatt.gatt_manager import gatt_hierarchy


class TestDataParsing:
    """Test data parsing functionality with simulated device data."""

    @pytest.fixture
    def simulated_nordic_thingy_services(self) -> dict:
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
    def simulated_nordic_thingy_data(self) -> dict[str, bytearray]:
        """Fixture providing simulated Nordic Thingy:52 characteristic data."""
        return {
            # Battery Level: 77 (0x4D)
            "00002a19-0000-1000-8000-00805f9b34fb": bytearray([0x4D]),
            # Temperature: simulated as sint16 = 2300 (23.00°C)
            "00002a6e-0000-1000-8000-00805f9b34fb": bytearray([0xFC, 0x08]),
            # Humidity: simulated as uint16 = 6100 (61.00%)
            "00002a6f-0000-1000-8000-00805f9b34fb": bytearray([0xD4, 0x17]),
            # Pressure: simulated as uint32 = 101325 Pa (sea level) - corrected bytes
            "00002a6d-0000-1000-8000-00805f9b34fb": bytearray([0xCD, 0x8B, 0x01, 0x00]),
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
        assert (
            len(gatt_hierarchy.discovered_services) > 0
        ), "No services were recognized"

        # Verify expected service count (should recognize at least Battery and Environmental)
        assert (
            len(gatt_hierarchy.discovered_services) >= 2
        ), f"Expected at least 2 services, got {len(gatt_hierarchy.discovered_services)}"

    def test_battery_level_parsing(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
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
                        assert (
                            parsed_value == 77
                        ), f"Expected battery level 77, got {parsed_value}"
                        assert (
                            characteristic.unit == "%"
                        ), f"Expected unit '%', got '{characteristic.unit}'"
                        battery_char = characteristic
                        break
                break

        assert battery_char is not None, "Battery level characteristic not found"

    def test_temperature_parsing(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
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
                        assert (
                            parsed_value == 23.0
                        ), f"Expected temperature 23.0°C, got {parsed_value}"
                        assert (
                            characteristic.unit == "°C"
                        ), f"Expected unit '°C', got '{characteristic.unit}'"
                        temp_char = characteristic
                        break
                break

        assert temp_char is not None, "Temperature characteristic not found"

    def test_humidity_parsing(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
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
                        assert (
                            parsed_value == 61.0
                        ), f"Expected humidity 61.0%, got {parsed_value}"
                        assert (
                            characteristic.unit == "%"
                        ), f"Expected unit '%', got '{characteristic.unit}'"
                        humidity_char = characteristic
                        break
                break

        assert humidity_char is not None, "Humidity characteristic not found"

    def test_pressure_parsing(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
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
                        assert (
                            parsed_value == 101.325
                        ), f"Expected pressure 101.325 kPa, got {parsed_value}"
                        assert (
                            characteristic.unit == "kPa"
                        ), f"Expected unit 'kPa', got '{characteristic.unit}'"
                        pressure_char = characteristic
                        break
                break

        assert pressure_char is not None, "Pressure characteristic not found"

    def test_device_info_parsing(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
        """Test device information characteristic parsing."""
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)

        # Find device info service
        device_service = None
        for service in gatt_hierarchy.discovered_services:
            if (
                "Device" in service.__class__.__name__
                or "Information" in service.__class__.__name__
            ):
                device_service = service
                break

        assert device_service is not None, "Device information service not found"

        # Test that device info characteristics exist
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

        assert (
            found_chars >= 1
        ), f"Expected to parse at least 1 device info characteristic, got {found_chars}"

    def test_comprehensive_parsing_count(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
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
                            characteristic.parse_value(data)  # Just test parsing
                            parsed_count += 1
                        except Exception:
                            # Some characteristics might fail to parse with test data
                            pass
                        break

        # We should be able to parse at least 4 characteristics (battery, temp, humidity, pressure)
        assert (
            parsed_count >= 4
        ), f"Expected to parse at least 4 characteristics, got {parsed_count}"
        assert (
            total_characteristics >= 6
        ), f"Expected at least 6 total characteristics, got {total_characteristics}"

    def test_comprehensive_characteristic_parsing_with_validation(
        self, simulated_nordic_thingy_services, simulated_nordic_thingy_data
    ):
        """Test comprehensive parsing of all characteristics with detailed validation.

        This test replicates the functionality from scripts/test_parsing.py
        ensuring that all characteristics can be parsed and validated.
        """
        # Reset and process services
        gatt_hierarchy._services = {}
        gatt_hierarchy.process_services(simulated_nordic_thingy_services)

        assert len(gatt_hierarchy.discovered_services) > 0, "No services recognized"

        parsed_count = 0
        error_count = 0
        missing_data_count = 0
        validation_results = {}

        for service in gatt_hierarchy.discovered_services:
            service_name = service.__class__.__name__
            validation_results[service_name] = {
                "characteristics": {},
                "total_chars": len(service.characteristics),
            }

            for char_uuid, characteristic in service.characteristics.items():
                char_name = characteristic.__class__.__name__

                # Find corresponding data using UUID matching logic from test_parsing.py
                found_data = False
                for data_uuid, raw_data in simulated_nordic_thingy_data.items():
                    if data_uuid.replace("-", "").upper() == char_uuid:
                        found_data = True
                        try:
                            parsed_value = characteristic.parse_value(raw_data)
                            unit = getattr(characteristic, "unit", "")

                            validation_results[service_name]["characteristics"][
                                char_name
                            ] = {
                                "status": "success",
                                "value": parsed_value,
                                "unit": unit,
                                "data_length": len(raw_data),
                            }
                            parsed_count += 1

                            # Additional validation based on characteristic type
                            if "BatteryLevel" in char_name:
                                assert isinstance(
                                    parsed_value, int
                                ), f"Battery level should be int, got {type(parsed_value)}"
                                assert (
                                    0 <= parsed_value <= 100
                                ), f"Battery level {parsed_value} out of range"
                                assert (
                                    unit == "%"
                                ), f"Battery level unit should be %, got {unit}"
                            elif "Temperature" in char_name:
                                assert isinstance(
                                    parsed_value, (int, float)
                                ), f"Temperature should be numeric, got {type(parsed_value)}"
                                assert (
                                    unit == "°C"
                                ), f"Temperature unit should be °C, got {unit}"
                            elif "Humidity" in char_name:
                                assert isinstance(
                                    parsed_value, (int, float)
                                ), f"Humidity should be numeric, got {type(parsed_value)}"
                                assert (
                                    unit == "%"
                                ), f"Humidity unit should be %, got {unit}"
                            elif "Pressure" in char_name:
                                assert isinstance(
                                    parsed_value, (int, float)
                                ), f"Pressure should be numeric, got {type(parsed_value)}"
                                assert unit in [
                                    "Pa",
                                    "hPa",
                                    "kPa",
                                ], f"Pressure unit should be Pa, hPa, or kPa, got {unit}"

                        except Exception as e:
                            validation_results[service_name]["characteristics"][
                                char_name
                            ] = {
                                "status": "error",
                                "error": str(e),
                                "data_length": len(raw_data),
                            }
                            error_count += 1
                        break

                if not found_data:
                    validation_results[service_name]["characteristics"][char_name] = {
                        "status": "no_data",
                        "uuid": char_uuid,
                    }
                    missing_data_count += 1

        # Comprehensive assertions
        assert (
            parsed_count >= 4
        ), f"Expected to parse at least 4 characteristics, got {parsed_count}"
        assert error_count == 0, f"No parsing errors expected, got {error_count} errors"

        # Verify specific characteristics were parsed successfully
        expected_characteristics = ["BatteryLevel", "Temperature", "Humidity"]
        found_expected = []

        for _service_name, service_data in validation_results.items():
            for char_name, char_data in service_data["characteristics"].items():
                if char_data["status"] == "success":
                    for expected in expected_characteristics:
                        if expected in char_name and expected not in found_expected:
                            found_expected.append(expected)

        assert (
            len(found_expected) >= 3
        ), f"Expected to find at least 3 key characteristics, found: {found_expected}"

        # Verify service recognition
        service_names = list(validation_results.keys())
        assert any(
            "Battery" in name for name in service_names
        ), "Battery service should be recognized"
        assert any(
            "Environmental" in name for name in service_names
        ), "Environmental service should be recognized"
