"""Tests for the Device class functionality."""

from __future__ import annotations

from typing import Any, Callable, cast

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.types.device_types import DeviceEncryption
from bluetooth_sig.types.uuid import BluetoothUUID


class MockConnectionManager:
    """Mock connection manager for testing."""

    def __init__(self, connected: bool = False) -> None:
        self.address = "AA:BB:CC:DD:EE:FF"
        self._connected = connected

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    # Synchronous helpers for tests
    def connect_sync(self) -> None:
        self._connected = True

    def disconnect_sync(self) -> None:
        self._connected = False

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        return b""

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes) -> None:
        pass

    async def get_services(self) -> Any:  # noqa: ANN401
        """Mock get_services - returns async."""
        return {}

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        """Mock start_notify with correct signature."""

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        pass


class FaultyManager:
    """Manager that raises when checking connection (used in tests)."""

    def __init__(self) -> None:
        self.address = "AA:BB:CC:DD:EE:FF"

    @property
    def is_connected(self) -> bool:
        raise RuntimeError("Connection check failed")


class IncompleteManager:
    """Manager missing protocol methods used to test fallback behavior."""

    def __init__(self) -> None:
        self.address = "AA:BB:CC:DD:EE:FF"


class NoneManager:
    """Manager that returns False for is_connected (used in tests)."""

    def __init__(self) -> None:
        self.address = "AA:BB:CC:DD:EE:FF"

    @property
    def is_connected(self) -> bool:
        return False


class TestDevice:
    """Test cases for the Device class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.translator = BluetoothSIGTranslator()
        self.device_address = "AA:BB:CC:DD:EE:FF"
        self.device = Device(self.device_address, self.translator)

    def test_device_initialization(self) -> None:
        """Test Device initialization."""
        assert self.device.address == self.device_address
        assert self.device.translator == self.translator
        assert self.device.name == ""
        assert self.device.services == {}
        assert isinstance(self.device.encryption, DeviceEncryption)
        assert self.device.advertiser_data is not None

    def test_device_string_representation(self) -> None:
        """Test Device string representation."""
        expected = f"Device({self.device_address}, name=, 0 services, 0 characteristics)"
        assert str(self.device) == expected

        # Test with name and services
        self.device.name = "Test Device"
        expected = f"Device({self.device_address}, name=Test Device, 0 services, 0 characteristics)"
        assert str(self.device) == expected

    def test_parse_advertiser_data_basic(self) -> None:
        """Test basic advertiser data parsing."""
        # Sample advertisement data with local name
        adv_data = bytes(
            [
                0x02,
                0x01,
                0x06,  # Flags: 0x06
                0x0C,
                0x09,
                0x54,
                0x65,
                0x73,
                0x74,
                0x20,
                0x44,
                0x65,
                0x76,
                0x69,
                0x63,
                0x65,  # Complete Local Name: "Test Device"
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert self.device.advertiser_data.raw_data == adv_data
        assert self.device.advertiser_data.parsed_structures.local_name == "Test Device"
        assert self.device.advertiser_data.parsed_structures.flags == 0x06
        assert self.device.name == "Test Device"  # Should update device name

    def test_parse_advertiser_data_manufacturer(self) -> None:
        """Test advertiser data parsing with manufacturer data."""
        # Sample advertisement data with manufacturer data
        adv_data = bytes(
            [
                0x06,
                0xFF,
                0x4C,
                0x00,
                0x01,
                0x02,
                0x03,  # Manufacturer data: Company ID 0x004C (Apple), data [0x01, 0x02, 0x03]
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert self.device.advertiser_data.parsed_structures.manufacturer_data[0x004C] == b"\x01\x02\x03"

    def test_parse_advertiser_data_service_uuids(self) -> None:
        """Test advertiser data parsing with service UUIDs."""
        # Sample advertisement data with 16-bit service UUIDs
        adv_data = bytes(
            [
                0x03,
                0x02,
                0x0F,
                0x18,  # Complete List of 16-bit Service UUIDs: 0x180F (Battery Service)
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert "180F" in self.device.advertiser_data.parsed_structures.service_uuids

    def test_parse_advertiser_data_tx_power(self) -> None:
        """Test advertiser data parsing with TX power."""
        # Sample advertisement data with TX power
        adv_data = bytes(
            [
                0x02,
                0x0A,
                0xFC,  # TX Power Level: -4 dBm
            ]
        )

        self.device.parse_advertiser_data(adv_data)

        assert self.device.advertiser_data is not None
        assert self.device.advertiser_data.parsed_structures.tx_power == -4

    def test_add_service_known_service(self) -> None:
        """Test adding a service with known service type."""
        # Battery service characteristics
        characteristics = {
            "2A19": b"\x64",  # Battery Level: 100%
        }

        self.device.add_service("180F", characteristics)

        assert "180F" in self.device.services
        service = self.device.services["180F"]
        assert len(service.characteristics) == 1
        assert "2A19" in service.characteristics

        # Check parsed data
        battery_data = service.characteristics["2A19"]
        assert battery_data.value == 100
        assert battery_data.name == "Battery Level"

    def test_add_service_unknown_service(self) -> None:
        """Test adding a service with unknown service name raises ValueError."""
        # Unknown service name that's not a valid UUID (contains non-hex characters)
        characteristics = {
            "1234": b"\x01\x02\x03",
        }

        # Should raise ValueError for unknown service name that's not a UUID
        with pytest.raises(ValueError, match="Cannot resolve service UUID for 'InvalidServiceName'"):
            self.device.add_service("InvalidServiceName", characteristics)

    def test_add_service_with_unknown_uuid(self) -> None:
        """Test adding a service with a valid UUID that's not in the registry creates UnknownService."""
        # Use a valid UUID format that's not a known service
        unknown_uuid = "ABCD"  # Valid 16-bit UUID, but not a known service
        characteristics = {
            "1234": b"\x01\x02\x03",
        }

        self.device.add_service(unknown_uuid, characteristics)

        # Should create an entry with the UUID as the key
        assert unknown_uuid in self.device.services
        service = self.device.services[unknown_uuid]
        # The service should be an UnknownService
        assert service.service.__class__.__name__ == "UnknownService"
        assert len(service.characteristics) == 1

    def test_get_characteristic_data(self) -> None:
        """Test retrieving characteristic data."""
        # Add a service first
        characteristics = {
            "2A19": b"\x64",  # Battery Level: 100%
        }
        self.device.add_service("180F", characteristics)

        # Retrieve the data
        data = self.device.get_characteristic_data("180F", "2A19")
        assert data is not None
        assert data.value == 100

        # Test non-existent service/characteristic
        assert self.device.get_characteristic_data("9999", "9999") is None
        assert self.device.get_characteristic_data("180F", "9999") is None

    def test_update_encryption_requirements(self) -> None:
        """Test encryption requirements tracking."""
        from bluetooth_sig.types import CharacteristicData, CharacteristicInfo
        from bluetooth_sig.types.gatt_enums import GattProperty
        from bluetooth_sig.types.uuid import BluetoothUUID

        # Create mock characteristic info with encryption properties
        char_info = CharacteristicInfo(
            uuid=BluetoothUUID("2A19"),
            name="Battery Level",
            properties=[GattProperty.READ, GattProperty.ENCRYPT_READ],
        )

        # Create characteristic data
        char_data = CharacteristicData(
            info=char_info,
            value=100,
        )

        self.device.update_encryption_requirements(char_data)

        assert self.device.encryption.requires_encryption is True

        # Test authentication requirement
        char_info_auth = CharacteristicInfo(
            uuid=BluetoothUUID("2A19"),
            name="Battery Level",
            properties=[GattProperty.READ, GattProperty.AUTH_READ],
        )

        char_data_auth = CharacteristicData(
            info=char_info_auth,
            value=100,
        )

        self.device.update_encryption_requirements(char_data_auth)

        assert self.device.encryption.requires_authentication is True

    def test_device_with_advertiser_context(self) -> None:
        """Test device functionality with advertiser data context."""
        # Set up advertiser data first
        adv_data = bytes(
            [
                0x02,
                0x01,
                0x06,  # Flags
                0x0C,
                0x09,
                0x54,
                0x65,
                0x73,
                0x74,
                0x20,
                0x44,
                0x65,
                0x76,
                0x69,
                0x63,
                0x65,  # Local Name
                0x06,
                0xFF,
                0x4C,
                0x00,
                0x01,
                0x02,
                0x03,  # Manufacturer data
            ]
        )
        self.device.parse_advertiser_data(adv_data)

        # Add service - should use advertiser context
        characteristics = {
            "2A19": b"\x64",  # Battery Level
        }
        self.device.add_service("180F", characteristics)

        # Verify service was added and context was used
        assert "180F" in self.device.services
        assert self.device.name == "Test Device"

    def test_is_connected_property(self) -> None:
        """Test is_connected property behavior."""
        # Test with no connection manager
        assert self.device.is_connected is False

        # Test with disconnected connection manager
        mock_manager = MockConnectionManager(connected=False)
        self.device.attach_connection_manager(mock_manager)
        assert self.device.is_connected is False

        # Test with connected connection manager
        mock_manager = MockConnectionManager(connected=True)
        self.device.attach_connection_manager(mock_manager)
        assert self.device.is_connected is True

    def test_is_connected_edge_cases(self) -> None:
        """Test is_connected property edge cases."""
        # Test connection manager state change
        mock_manager = MockConnectionManager(connected=True)
        self.device.attach_connection_manager(mock_manager)
        assert self.device.is_connected is True

        # Change state through manager using provided synchronous helper
        mock_manager.disconnect_sync()
        assert self.device.is_connected is False

    # Test None return value from manager is handled in separate test

    def test_is_connected_error_handling(self) -> None:
        """Test is_connected property error handling."""
        # Test manager that raises exception - use module-level FaultyManager
        faulty_manager = FaultyManager()
        # cast to ConnectionManagerProtocol to satisfy static type checking
        self.device.attach_connection_manager(cast(ConnectionManagerProtocol, faulty_manager))

        # Should propagate the exception
        with pytest.raises(RuntimeError, match="Connection check failed"):
            _ = self.device.is_connected

        # Test manager without is_connected property - use module-level IncompleteManager
        incomplete_manager = IncompleteManager()
        self.device.attach_connection_manager(cast(ConnectionManagerProtocol, incomplete_manager))

        # Should return False for manager without is_connected property
        assert self.device.is_connected is False

    def test_is_connected_with_none_manager(self) -> None:
        """Test is_connected returns False when manager's is_connected returns
        False.
        """
        none_manager = NoneManager()
        self.device.attach_connection_manager(cast(ConnectionManagerProtocol, none_manager))
        assert self.device.is_connected is False

    def test_connection_manager_protocol_interface(self) -> None:
        """Test that ConnectionManagerProtocol has the is_connected
        property.
        """
        import inspect

        # Check that is_connected is part of the protocol interface
        members = inspect.getmembers(ConnectionManagerProtocol)
        protocol_attrs = [name for name, _ in members if not name.startswith("_")]

        # Verify is_connected is in the protocol
        assert "is_connected" in protocol_attrs

        # Verify other expected methods are also present
        expected_methods = [
            "connect",
            "disconnect",
            "read_gatt_char",
            "write_gatt_char",
            "get_services",
            "start_notify",
            "stop_notify",
            "is_connected",
        ]
        for method in expected_methods:
            assert method in protocol_attrs, f"Method {method} missing from protocol"

    def test_device_info_caching(self) -> None:
        """Test that device info is cached and updated efficiently."""
        # First access creates cache
        device_info1 = self.device.device_info
        assert device_info1.address == self.device.address
        assert device_info1.name == ""

        # Second access uses same cached object (efficiency test)
        device_info2 = self.device.device_info
        assert device_info2 is device_info1

        # Changing name should update the cached object in place for efficiency
        self.device.name = "Test Device"
        device_info3 = self.device.device_info
        assert device_info3 is device_info1  # Same object reused (efficient)
        assert device_info3.name == "Test Device"  # But data updated

        # Parsing advertiser data should update the same cached object
        raw_advertising_data = bytes(
            [
                0x02,
                0x01,
                0x06,  # Flags
                0x03,
                0x02,
                0x0F,
                0x18,  # Complete list of 16-bit Service UUIDs: Battery Service (180F)
                0x05,
                0xFF,
                0x4C,
                0x00,
                0x01,
                0x02,  # Manufacturer data: Apple (0x004C), data: 01 02
            ]
        )

        self.device.parse_advertiser_data(raw_advertising_data)
        device_info4 = self.device.device_info
        assert device_info4 is device_info1  # Still same object (efficient)
        assert device_info4.name == "Test Device"  # Name remains (not overwritten by advertiser)
        assert "180F" in device_info4.service_uuids  # Service UUID from advertiser data
        assert 76 in device_info4.manufacturer_data  # Manufacturer data from advertiser
