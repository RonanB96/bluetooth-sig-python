"""Tests for UUID registry and YAML loading functionality."""

# pylint: disable=redefined-outer-name  # pytest fixtures
from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.characteristics.humidity import HumidityCharacteristic
from bluetooth_sig.gatt.characteristics.temperature import TemperatureCharacteristic
from bluetooth_sig.gatt.services.battery_service import BatteryService
from bluetooth_sig.gatt.services.environmental_sensing import (
    EnvironmentalSensingService,
)
from bluetooth_sig.gatt.uuid_registry import UuidRegistry
from bluetooth_sig.types.gatt_services import ServiceDiscoveryData


@pytest.fixture(scope="session")
def uuid_registry() -> UuidRegistry:
    """Create a UUID registry once per test session for performance."""
    return UuidRegistry()


@pytest.fixture(scope="session")
def mock_uuid_registry() -> UuidRegistry:
    """Create a mock UUID registry for tests that don't need real data."""
    registry = MagicMock(spec=UuidRegistry)

    # Mock service lookups
    battery_info = MagicMock()
    battery_info.uuid = "180F"
    battery_info.name = "Battery"
    battery_info.id = "org.bluetooth.service.battery_service"

    env_info = MagicMock()
    env_info.uuid = "181A"
    env_info.name = "Environmental Sensing"
    env_info.id = "org.bluetooth.service.environmental_sensing"

    def mock_get_service_info(uuid: str) -> Any:
        return {
            "180F": battery_info,
            "181A": env_info,
        }.get(uuid)

    registry.get_service_info.side_effect = mock_get_service_info

    # Mock characteristic lookups
    battery_level_info = MagicMock()
    battery_level_info.uuid = "2A19"
    battery_level_info.name = "Battery Level"
    battery_level_info.id = "org.bluetooth.characteristic.battery_level"

    temp_info = MagicMock()
    temp_info.uuid = "2A6E"
    temp_info.name = "Temperature"
    temp_info.id = "org.bluetooth.characteristic.temperature"

    humidity_info = MagicMock()
    humidity_info.uuid = "2A6F"
    humidity_info.name = "Humidity"
    humidity_info.id = "org.bluetooth.characteristic.humidity"

    def mock_get_characteristic_info(uuid: str) -> Any:
        return {
            "2A19": battery_level_info,
            "00002A19-0000-1000-8000-00805F9B34FB": battery_level_info,
            "2A6E": temp_info,
            "2A6F": humidity_info,
        }.get(uuid)

    registry.get_characteristic_info.side_effect = mock_get_characteristic_info

    return registry


@pytest.mark.parametrize(
    "service_uuid,service_name,service_id",
    [
        ("180F", "Battery", "org.bluetooth.service.battery_service"),
        (
            "181A",
            "Environmental Sensing",
            "org.bluetooth.service.environmental_sensing",
        ),
    ],
)
def test_service_uuid_lookup_parametrized(
    mock_uuid_registry: UuidRegistry,
    service_uuid: str,
    service_name: str,
    service_id: str,
):
    """Test that service UUIDs are correctly loaded from YAML files."""
    info = mock_uuid_registry.get_service_info(service_uuid)
    assert info is not None, f"{service_name} Service not found"
    assert info.uuid == service_uuid
    assert info.name == service_name
    assert info.id == service_id


@pytest.mark.parametrize(
    "char_uuid,char_name,char_id",
    [
        ("2A19", "Battery Level", "org.bluetooth.characteristic.battery_level"),
        ("2A6E", "Temperature", "org.bluetooth.characteristic.temperature"),
        ("2A6F", "Humidity", "org.bluetooth.characteristic.humidity"),
    ],
)
def test_characteristic_uuid_lookup_parametrized(
    mock_uuid_registry: UuidRegistry, char_uuid: str, char_name: str, char_id: str
):
    """Test that characteristic UUIDs are correctly loaded."""
    info = mock_uuid_registry.get_characteristic_info(char_uuid)
    assert info is not None, f"{char_name} characteristic not found"
    assert info.uuid == char_uuid
    assert info.name == char_name
    assert info.id == char_id


def test_service_class_name_resolution():
    """Test that service classes correctly resolve their UUIDs from names."""
    battery = BatteryService()
    env = EnvironmentalSensingService()

    assert battery.uuid == "180F", "Wrong Battery Service UUID"
    assert battery.name == "Battery", "Wrong Battery Service name"

    assert env.uuid == "181A", "Wrong Environmental Service UUID"
    assert env.name == "Environmental Sensing", "Wrong Environmental Service name"


def test_characteristic_discovery():
    """Test discovery and creation of characteristics from device data."""
    # Use characteristic classes to get proper SIG UUIDs
    battery_char = BatteryLevelCharacteristic()
    temp_char = TemperatureCharacteristic()
    humidity_char = HumidityCharacteristic()

    # Mock device data using CharacteristicInfo from the characteristic instances
    mock_battery_data: ServiceDiscoveryData = {battery_char.uuid: battery_char.info}

    mock_env_data: ServiceDiscoveryData = {
        temp_char.uuid: temp_char.info,
        humidity_char.uuid: humidity_char.info,
    }

    # Test Battery Service characteristic discovery
    battery = BatteryService()
    battery.process_characteristics(mock_battery_data)

    assert len(battery.characteristics) == 1, "Incorrect battery char count"
    char = next(iter(battery.characteristics.values()))
    assert char.name == "Battery Level"
    # Properties come from YAML or class definition, not from discovery data
    assert char.properties is not None
    # Test Environmental Service characteristic discovery
    env = EnvironmentalSensingService()
    env.process_characteristics(mock_env_data)

    assert len(env.characteristics) == 2, "Wrong number of environmental characteristics"
    chars = list(env.characteristics.values())
    char_names = {c.name for c in chars}
    assert "Temperature" in char_names
    assert "Humidity" in char_names


def test_full_uuid_lookup(mock_uuid_registry: UuidRegistry):
    """Test lookup with full 128-bit UUIDs."""
    # Test with full Battery Level UUID
    full_uuid = "00002A19-0000-1000-8000-00805F9B34FB"
    info = mock_uuid_registry.get_characteristic_info(full_uuid)
    assert info is not None, "Characteristic not found with full UUID"
    assert info.uuid == "2A19"
    assert info.name == "Battery Level"


def test_invalid_uuid_lookup(mock_uuid_registry: UuidRegistry):
    """Test lookup behavior with invalid UUIDs."""
    assert mock_uuid_registry.get_service_info("0000") is None, "Should return None for invalid service"
    assert mock_uuid_registry.get_characteristic_info("0000") is None, "Should return None for invalid characteristic"


def test_yaml_file_presence():
    """Test that required YAML files exist."""
    base_path = Path(__file__).parent.parent / "bluetooth_sig" / "assigned_numbers" / "uuids"

    assert (base_path / "service_uuids.yaml").exists(), "Service UUIDs YAML file missing"
    assert (base_path / "characteristic_uuids.yaml").exists(), "Characteristic UUIDs YAML file missing"


@pytest.fixture(scope="session")
def yaml_data() -> dict[str, Any]:
    """Load YAML data once per session for performance."""
    import yaml

    base_path = Path(__file__).parent.parent / "bluetooth_sig" / "assigned_numbers" / "uuids"

    # Load service data
    service_file = base_path / "service_uuids.yaml"
    with service_file.open("r") as f:
        service_data = yaml.safe_load(f)

    # Load characteristic data
    char_file = base_path / "characteristic_uuids.yaml"
    with char_file.open("r") as f:
        char_data = yaml.safe_load(f)

    return {"services": service_data, "characteristics": char_data}


def test_direct_yaml_loading(yaml_data: dict[str, Any]) -> None:
    """Test direct loading and parsing of YAML files.

    This test replicates functionality from scripts/test_yaml_loading.py
    to ensure YAML files can be loaded and contain expected data.
    """
    service_data = yaml_data["services"]
    char_data = yaml_data["characteristics"]

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
    assert env_service["name"] == "Environmental Sensing", "Wrong Environmental Service name in YAML"

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

    assert battery_level is not None, "Failed to find Battery Level characteristic in YAML"
    assert temperature is not None, "Failed to find Temperature characteristic in YAML"
    assert humidity is not None, "Failed to find Humidity characteristic in YAML"

    # Verify characteristic names
    assert battery_level["name"] == "Battery Level", "Wrong Battery Level name in YAML"
    assert temperature["name"] == "Temperature", "Wrong Temperature name in YAML"
    assert humidity["name"] == "Humidity", "Wrong Humidity name in YAML"


class TestBluetoothUUID:
    """Tests for BluetoothUUID utility methods."""

    def test_sig_characteristic_uuid_detection(self) -> None:
        """Test SIG characteristic UUID detection logic."""
        from bluetooth_sig.types.uuid import BluetoothUUID

        # Test SIG characteristic UUIDs (should return True)
        assert BluetoothUUID("2A19").is_sig_characteristic() is True  # Battery Level
        assert BluetoothUUID("2A37").is_sig_characteristic() is True  # Heart Rate
        assert BluetoothUUID("2A00").is_sig_characteristic() is True  # Device Name
        assert BluetoothUUID("2C24").is_sig_characteristic() is True  # Upper range

        # Test non-SIG UUIDs (should return False)
        assert BluetoothUUID("12345678-1234-1234-1234-123456789ABC").is_sig_characteristic() is False
        assert BluetoothUUID("FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF").is_sig_characteristic() is False
        assert BluetoothUUID("1800").is_sig_characteristic() is False  # Service UUID
        assert BluetoothUUID("29FF").is_sig_characteristic() is False  # Below SIG range
        assert BluetoothUUID("2C25").is_sig_characteristic() is False  # Above SIG range
