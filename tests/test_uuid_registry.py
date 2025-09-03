"""Tests for UUID registry and YAML loading functionality."""

# pylint: disable=redefined-outer-name  # pytest fixtures

from pathlib import Path

import pytest

from bluetooth_sig.gatt.services.battery_service import BatteryService
from bluetooth_sig.gatt.services.environmental_sensing import (
    EnvironmentalSensingService,
)
from bluetooth_sig.gatt.uuid_registry import UuidRegistry


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
    assert env.name == "Environmental Sensing", "Wrong Environmental Service name"


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

    assert len(env.characteristics) == 2, (
        "Wrong number of environmental characteristics"
    )
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
    assert uuid_registry.get_service_info("0000") is None, (
        "Should return None for invalid service"
    )
    assert uuid_registry.get_characteristic_info("0000") is None, (
        "Should return None for invalid characteristic"
    )


def test_yaml_file_presence():
    """Test that required YAML files exist."""
    base_path = (
        Path(__file__).parent.parent / "bluetooth_sig" / "assigned_numbers" / "uuids"
    )

    assert (base_path / "service_uuids.yaml").exists(), (
        "Service UUIDs YAML file missing"
    )
    assert (base_path / "characteristic_uuids.yaml").exists(), (
        "Characteristic UUIDs YAML file missing"
    )


def test_direct_yaml_loading():
    """Test direct loading and parsing of YAML files.

    This test replicates functionality from scripts/test_yaml_loading.py
    to ensure YAML files can be loaded and contain expected data.
    """
    import yaml

    base_path = (
        Path(__file__).parent.parent / "bluetooth_sig" / "assigned_numbers" / "uuids"
    )

    # Test Service UUIDs file loading
    service_file = base_path / "service_uuids.yaml"
    with service_file.open("r") as f:
        service_data = yaml.safe_load(f)

    assert "uuids" in service_data, "Service YAML should have 'uuids' key"
    assert isinstance(service_data["uuids"], list), "Service UUIDs should be a list"

    # Find specific services
    battery_service = None
    env_service = None

    for service in service_data["uuids"]:
        # Handle both string and integer UUID formats
        if isinstance(service["uuid"], str):
            uuid = service["uuid"].replace("0x", "")
        else:
            uuid = hex(service["uuid"])[2:].upper()

        if uuid == "180F":  # Battery Service
            battery_service = service
        elif uuid == "181A":  # Environmental Sensing
            env_service = service

    assert battery_service is not None, "Failed to find Battery Service in YAML"
    assert env_service is not None, "Failed to find Environmental Service in YAML"
    assert battery_service["name"] == "Battery", "Wrong Battery Service name in YAML"
    assert env_service["name"] == "Environmental Sensing", (
        "Wrong Environmental Service name in YAML"
    )

    # Test Characteristic UUIDs file loading
    char_file = base_path / "characteristic_uuids.yaml"
    with char_file.open("r") as f:
        char_data = yaml.safe_load(f)

    assert "uuids" in char_data, "Characteristic YAML should have 'uuids' key"
    assert isinstance(char_data["uuids"], list), "Characteristic UUIDs should be a list"

    # Find specific characteristics
    battery_level = None
    temperature = None
    humidity = None

    for char in char_data["uuids"]:
        # Handle both string and integer UUID formats
        if isinstance(char["uuid"], str):
            uuid = char["uuid"].replace("0x", "")
        else:
            uuid = hex(char["uuid"])[2:].upper()

        if uuid == "2A19":  # Battery Level
            battery_level = char
        elif uuid == "2A6E":  # Temperature
            temperature = char
        elif uuid == "2A6F":  # Humidity
            humidity = char

    assert battery_level is not None, (
        "Failed to find Battery Level characteristic in YAML"
    )
    assert temperature is not None, "Failed to find Temperature characteristic in YAML"
    assert humidity is not None, "Failed to find Humidity characteristic in YAML"

    # Verify characteristic names
    assert battery_level["name"] == "Battery Level", "Wrong Battery Level name in YAML"
    assert temperature["name"] == "Temperature", "Wrong Temperature name in YAML"
    assert humidity["name"] == "Humidity", "Wrong Humidity name in YAML"
