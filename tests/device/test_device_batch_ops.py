"""Tests for Device batch operations and service discovery.

Tests for:
- discover_services()
- get_characteristic_info()
- read_multiple()
- write_multiple()
- connect() / disconnect()
"""

from __future__ import annotations

from typing import Callable
from unittest.mock import MagicMock

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.gatt.services.battery_service import BatteryService
from bluetooth_sig.types.advertising.ad_structures import AdvertisingDataStructures, CoreAdvertisingData
from bluetooth_sig.types.advertising.result import AdvertisementData
from bluetooth_sig.types.device_types import DeviceService
from bluetooth_sig.types.gatt_enums import CharacteristicName
from bluetooth_sig.types.uuid import BluetoothUUID


class ServiceMockConnectionManager(ConnectionManagerProtocol):
    """Mock connection manager with service discovery support."""

    def __init__(
        self,
        address: str = "AA:BB:CC:DD:EE:FF",
        connected: bool = True,
        **kwargs: object,
    ) -> None:
        """Initialize mock connection manager."""
        super().__init__(address, **kwargs)
        self._connected = connected
        self._mtu = 247

        # Configurable services
        self._services: list[DeviceService] = []

        # Track read/write calls
        self.read_calls: list[BluetoothUUID] = []
        self.write_calls: list[tuple[BluetoothUUID, bytes, bool]] = []
        self.read_responses: dict[str, bytes] = {}

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def mtu_size(self) -> int:
        return self._mtu

    @property
    def name(self) -> str:
        return "Service Mock Device"

    async def connect(self, *, timeout: float = 10.0) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        self.read_calls.append(char_uuid)
        uuid_str = str(char_uuid)
        return self.read_responses.get(uuid_str, b"\x64")

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        self.write_calls.append((char_uuid, data, response))

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        return b"\x00\x00"

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        pass

    async def get_services(self) -> list[DeviceService]:
        return self._services

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        pass

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        pass

    async def pair(self) -> None:
        pass

    async def unpair(self) -> None:
        pass

    async def read_rssi(self) -> int:
        return -55

    async def get_advertisement_rssi(self, refresh: bool = False) -> int | None:
        return -65

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        pass

    @classmethod
    def convert_advertisement(cls, _advertisement: object) -> AdvertisementData:
        return AdvertisementData(
            ad_structures=AdvertisingDataStructures(core=CoreAdvertisingData()),
        )

    async def get_latest_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        return None


@pytest.fixture
def device_with_manager() -> tuple[Device, ServiceMockConnectionManager]:
    """Create device with attached mock connection manager."""
    translator = BluetoothSIGTranslator()
    manager = ServiceMockConnectionManager(connected=False)
    device = Device(manager, translator)
    return device, manager


class TestDeviceConnectDisconnect:
    """Tests for Device connect/disconnect methods."""

    @pytest.mark.asyncio
    async def test_connect(self, device_with_manager: tuple[Device, ServiceMockConnectionManager]) -> None:
        """Test connecting to device."""
        device, manager = device_with_manager
        await manager.disconnect()
        assert manager.is_connected is False

        await device.connect()

        assert manager.is_connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self, device_with_manager: tuple[Device, ServiceMockConnectionManager]) -> None:
        """Test disconnecting from device."""
        device, manager = device_with_manager
        await manager.connect()
        assert manager.is_connected is True

        await device.disconnect()

        assert manager.is_connected is False


class TestDeviceServiceDiscovery:
    """Tests for Device service discovery."""

    @pytest.mark.asyncio
    async def test_discover_services_empty(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test discovering services when device has none."""
        device, manager = device_with_manager
        manager._services = []

        services = await device.discover_services()

        assert services == {}

    @pytest.mark.asyncio
    async def test_discover_services_with_services(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test discovering services returns found services."""
        device, manager = device_with_manager

        # Create mock service
        mock_service = MagicMock(spec=DeviceService)
        mock_service.service = BatteryService()
        mock_service.characteristics = {}
        manager._services = [mock_service]

        services = await device.discover_services()

        assert len(services) == 1


class TestDeviceGetCharacteristicInfo:
    """Tests for Device.get_characteristic_info()."""

    @pytest.mark.asyncio
    async def test_get_characteristic_info_not_found(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test get_characteristic_info returns None when not found."""
        device, manager = device_with_manager
        manager._services = []

        result = await device.get_characteristic_info("2A19")

        assert result is None


class TestDeviceReadMultiple:
    """Tests for Device.read_multiple()."""

    @pytest.mark.asyncio
    async def test_read_multiple_success(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test reading multiple characteristics."""
        device, manager = device_with_manager

        _ = await device.read_multiple(["2A19", "2A00"])

        # Should have attempted to read both
        assert len(manager.read_calls) == 2

    @pytest.mark.asyncio
    async def test_read_multiple_partial_failure(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test read_multiple handles partial failures gracefully."""
        device, manager = device_with_manager

        # Make one read fail by storing a custom async function
        call_count = 0

        async def failing_read(char_uuid: BluetoothUUID) -> bytes:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Read failed")
            return b"\x64"

        # Use object.__setattr__ to bypass mypy method-assign check
        object.__setattr__(manager, "read_gatt_char", failing_read)

        results = await device.read_multiple(["2A19", "2A00"])

        # Should have results for both, one is None due to failure
        assert len(results) == 2
        # One should be None (failed), one should have a value

    @pytest.mark.asyncio
    async def test_read_multiple_empty_list(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test read_multiple with empty list."""
        device, manager = device_with_manager

        results = await device.read_multiple([])

        assert results == {}
        assert len(manager.read_calls) == 0


class TestDeviceWriteMultiple:
    """Tests for Device.write_multiple()."""

    @pytest.mark.asyncio
    async def test_write_multiple_success(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test writing multiple characteristics."""
        device, manager = device_with_manager
        data_map: dict[str | CharacteristicName, bytes] = {
            "2A19": b"\x50",
            "2A00": b"Device",
        }

        results = await device.write_multiple(data_map)

        assert len(manager.write_calls) == 2
        # All writes should succeed
        assert all(results.values())

    @pytest.mark.asyncio
    async def test_write_multiple_partial_failure(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test write_multiple handles partial failures gracefully."""
        device, manager = device_with_manager

        call_count = 0

        async def failing_write(char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Write failed")

        # Use object.__setattr__ to bypass mypy method-assign check
        object.__setattr__(manager, "write_gatt_char", failing_write)

        data_map: dict[str | CharacteristicName, bytes] = {
            "2A19": b"\x50",
            "2A00": b"Device",
        }

        results = await device.write_multiple(data_map)

        # Should have results for both
        assert len(results) == 2
        # One should be False (failed)
        assert not all(results.values())

    @pytest.mark.asyncio
    async def test_write_multiple_without_response(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test write_multiple with response=False."""
        device, manager = device_with_manager
        data_map: dict[str | CharacteristicName, bytes] = {"2A19": b"\x50"}

        await device.write_multiple(data_map, response=False)

        assert len(manager.write_calls) == 1
        _, _, response = manager.write_calls[0]
        assert response is False

    @pytest.mark.asyncio
    async def test_write_multiple_empty_map(
        self, device_with_manager: tuple[Device, ServiceMockConnectionManager]
    ) -> None:
        """Test write_multiple with empty map."""
        device, manager = device_with_manager

        results = await device.write_multiple({})

        assert results == {}
        assert len(manager.write_calls) == 0
