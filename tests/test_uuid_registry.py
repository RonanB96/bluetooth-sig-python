"""Tests for UUID registry and YAML loading functionality."""
# pylint: disable=redefined-outer-name  # pytest fixtures

from pathlib import Path
import pytest

from ble_gatt_device.gatt.uuid_registry import UuidRegistry
from ble_gatt_device.gatt.services.battery_service import BatteryService
from ble_gatt_device.gatt.services.environmental_sensing import (
    EnvironmentalSensingService,
)


@pytest.fixture
def uuid_registry():
    """Create a fresh UUID registry for each test."""
    return UuidRegistry()


def test_service_uuid_lookup(uuid_registry):
    """Test that service UUIDs are correctly loaded from YAML files."""
    # Test Battery Service
    info = uuid_registry.get_service_info("180F")
    assert info is not None, "Battery Service not found"
    assert info.uuid == "180F"
    assert info.name == "Battery"
    assert info.id == "org.bluetooth.service.battery_service"

    # Test Environmental Sensing Service
    info = uuid_registry.get_service_info("181A")
    assert info is not None, "Environmental Sensing Service not found"
    assert info.uuid == "181A"
    assert info.name == "Environmental Sensing"
    assert info.id == "org.bluetooth.service.environmental_sensing"


def test_characteristic_uuid_lookup(uuid_registry):
    """Test that characteristic UUIDs are correctly loaded."""
    # Test Battery Level characteristic
    info = uuid_registry.get_characteristic_info("2A19")
    assert info is not None, "Battery Level characteristic not found"
    assert info.uuid == "2A19"
    assert info.name == "Battery Level"
    assert info.id == "org.bluetooth.characteristic.battery_level"

    # Test Temperature characteristic
    info = uuid_registry.get_characteristic_info("2A6E")
    assert info is not None, "Temperature characteristic not found"
    assert info.uuid == "2A6E"
    assert info.name == "Temperature"
    assert info.id == "org.bluetooth.characteristic.temperature"

    # Test Humidity characteristic
    info = uuid_registry.get_characteristic_info("2A6F")
    assert info is not None, "Humidity characteristic not found"
    assert info.uuid == "2A6F"
    assert info.name == "Humidity"
    assert info.id == "org.bluetooth.characteristic.humidity"


def test_service_class_name_resolution():
    """Test that service classes correctly resolve their UUIDs from names."""
    battery = BatteryService()
    env = EnvironmentalSensingService()

    assert battery.SERVICE_UUID == "180F", "Wrong Battery Service UUID"
    assert battery.name == "Battery", "Wrong Battery Service name"

    assert env.SERVICE_UUID == "181A", "Wrong Environmental Service UUID"
    assert (
        env.name == "Environmental Sensing"
    ), "Wrong Environmental Service name"


def test_characteristic_discovery():
    """Test discovery and creation of characteristics from device data."""
    # Mock device data
    mock_battery_data = {
        "00002A19-0000-1000-8000-00805F9B34FB": {  # Battery Level
            "properties": ["read", "notify"]
        }
    }

    mock_env_data = {
        "00002A6E-0000-1000-8000-00805F9B34FB": {  # Temperature
            "properties": ["read", "notify"]
        },
        "00002A6F-0000-1000-8000-00805F9B34FB": {  # Humidity
            "properties": ["read", "notify"]
        },
    }

    # Test Battery Service characteristic discovery
    battery = BatteryService()
    battery.process_characteristics(mock_battery_data)

    assert len(battery.characteristics) == 1, "Incorrect battery char count"
    char = next(iter(battery.characteristics.values()))
    assert char.name == "Battery Level"
    assert "read" in char.properties
    assert "notify" in char.properties

    # Test Environmental Service characteristic discovery
    env = EnvironmentalSensingService()
    env.process_characteristics(mock_env_data)

    assert (
        len(env.characteristics) == 2
    ), "Wrong number of environmental characteristics"
    chars = list(env.characteristics.values())
    char_names = {c.name for c in chars}
    assert "Temperature" in char_names
    assert "Humidity" in char_names


def test_full_uuid_lookup(uuid_registry):
    """Test lookup with full 128-bit UUIDs."""
    # Test with full Battery Level UUID
    full_uuid = "00002A19-0000-1000-8000-00805F9B34FB"
    info = uuid_registry.get_characteristic_info(full_uuid)
    assert info is not None, "Characteristic not found with full UUID"
    assert info.uuid == "2A19"
    assert info.name == "Battery Level"


def test_invalid_uuid_lookup(uuid_registry):
    """Test lookup behavior with invalid UUIDs."""
    assert (
        uuid_registry.get_service_info("0000") is None
    ), "Should return None for invalid service"
    assert (
        uuid_registry.get_characteristic_info("0000") is None
    ), "Should return None for invalid characteristic"


def test_yaml_file_presence():
    """Test that required YAML files exist."""
    base_path = (
        (
            Path(__file__).parent.parent
            / "bluetooth_sig"
            / "assigned_numbers"
            / "uuids"
        )
    )

    assert (
        base_path / "service_uuids.yaml"
    ).exists(), "Service UUIDs YAML file missing"
    assert (
        base_path / "characteristic_uuids.yaml"
    ).exists(), "Characteristic UUIDs YAML file missing"
