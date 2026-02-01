"""Tests for Device async methods - runtime and functional tests.

Tests the Device class async methods including:
- read(), write()
- start_notify(), stop_notify()
- pair(), unpair()
- read_rssi()
- read_descriptor(), write_descriptor()
- set_disconnected_callback()
- mtu_size property
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.device.connection import ConnectionManagerProtocol
from bluetooth_sig.gatt.descriptors.cccd import CCCDDescriptor
from bluetooth_sig.types.advertising.ad_structures import AdvertisingDataStructures, CoreAdvertisingData
from bluetooth_sig.types.advertising.result import AdvertisementData
from bluetooth_sig.types.device_types import DeviceService
from bluetooth_sig.types.uuid import BluetoothUUID


# pylint: disable=too-many-instance-attributes  # Mock needs to track all protocol state
class AsyncMockConnectionManager(ConnectionManagerProtocol):
    """Mock connection manager with async method tracking."""

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

        # Track method calls
        self.read_char_calls: list[BluetoothUUID] = []
        self.write_char_calls: list[tuple[BluetoothUUID, bytes, bool]] = []
        self.notify_callbacks: dict[str, Callable[[str, bytes], None]] = {}
        self.stopped_notifications: list[BluetoothUUID] = []
        self.paired = False
        self.disconnected_callback: Callable[[], None] | None = None

        # Configurable return values
        self.read_char_return: bytes = b"\x64"  # Battery level 100%
        self.rssi_return: int = -55

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def mtu_size(self) -> int:
        return self._mtu

    @property
    def name(self) -> str:
        return "Async Mock Device"

    async def connect(self, *, timeout: float = 10.0) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False
        if self.disconnected_callback:
            self.disconnected_callback()

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        self.read_char_calls.append(char_uuid)
        return self.read_char_return

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        self.write_char_calls.append((char_uuid, data, response))

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        return b"\x00\x00"  # CCCD disabled

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        pass

    async def get_services(self) -> list[DeviceService]:
        return []

    async def start_notify(self, char_uuid: BluetoothUUID, callback: Callable[[str, bytes], None]) -> None:
        self.notify_callbacks[str(char_uuid)] = callback

    async def stop_notify(self, char_uuid: BluetoothUUID) -> None:
        self.stopped_notifications.append(char_uuid)

    async def pair(self) -> None:
        self.paired = True

    async def unpair(self) -> None:
        self.paired = False

    async def read_rssi(self) -> int:
        return self.rssi_return

    async def get_advertisement_rssi(self, refresh: bool = False) -> int | None:
        return -65

    def set_disconnected_callback(self, callback: Callable[[], None]) -> None:
        self.disconnected_callback = callback

    @classmethod
    def convert_advertisement(cls, _advertisement: object) -> AdvertisementData:
        return AdvertisementData(
            ad_structures=AdvertisingDataStructures(core=CoreAdvertisingData()),
        )

    async def get_latest_advertisement(self, refresh: bool = False) -> AdvertisementData | None:
        return None


@pytest.fixture
def device_with_manager() -> tuple[Device, AsyncMockConnectionManager]:
    """Create device with attached mock connection manager."""
    translator = BluetoothSIGTranslator()
    manager = AsyncMockConnectionManager()
    device = Device(manager, translator)
    return device, manager


class TestDeviceAsyncRead:
    """Tests for Device.read() async method."""

    @pytest.mark.asyncio
    async def test_read_by_uuid_string(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test reading characteristic by UUID string."""
        device, manager = device_with_manager
        manager.read_char_return = b"\x50"  # 80%

        result = await device.read("2A19")  # Battery Level characteristic UUID

        assert len(manager.read_char_calls) == 1
        assert result == 0x50  # Parsed battery level

    @pytest.mark.asyncio
    async def test_write_with_response(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test writing characteristic with response (default)."""
        device, manager = device_with_manager
        data = b"\x01\x02\x03"

        await device.write("2A19", data)  # Battery Level characteristic

        assert len(manager.write_char_calls) == 1
        _, written_data, response = manager.write_char_calls[0]
        assert written_data == data
        assert response is True

    @pytest.mark.asyncio
    async def test_write_without_response(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test writing characteristic without response."""
        device, manager = device_with_manager
        data = b"\x04\x05\x06"

        await device.write("2A19", data, response=False)

        assert len(manager.write_char_calls) == 1
        _, _, response = manager.write_char_calls[0]
        assert response is False

    @pytest.mark.asyncio
    async def test_start_notify(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test starting notifications for a characteristic."""
        device, manager = device_with_manager
        received_values: list[Any] = []

        def callback(value: Any) -> None:
            received_values.append(value)

        await device.start_notify("2A19", callback)

        # Verify notification was registered
        assert len(manager.notify_callbacks) == 1

    @pytest.mark.asyncio
    async def test_notification_callback_receives_parsed_data(
        self, device_with_manager: tuple[Device, AsyncMockConnectionManager]
    ) -> None:
        """Test that notification callback receives parsed data."""
        device, manager = device_with_manager
        received_values: list[Any] = []

        def callback(value: Any) -> None:
            received_values.append(value)

        await device.start_notify("2A19", callback)

        # Simulate notification by calling the internal callback
        internal_callback = next(iter(manager.notify_callbacks.values()))
        internal_callback("2A19", b"\x64")  # Battery level 100%

        assert len(received_values) == 1

    @pytest.mark.asyncio
    async def test_notification_callback_exception_logged(
        self, device_with_manager: tuple[Device, AsyncMockConnectionManager]
    ) -> None:
        """Test that exceptions in notification callback are logged but don't crash."""
        device, manager = device_with_manager

        def failing_callback(value: Any) -> None:
            raise ValueError("Callback error")

        await device.start_notify("2A19", failing_callback)

        # Simulate notification - should not raise
        internal_callback = next(iter(manager.notify_callbacks.values()))
        # This should log the exception but not propagate it
        internal_callback("2A19", b"\x64")


class TestDeviceAsyncPairing:
    """Tests for Device pairing methods."""

    @pytest.mark.asyncio
    async def test_pair(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test pairing with device."""
        device, manager = device_with_manager

        await device.pair()

        assert manager.paired is True

    @pytest.mark.asyncio
    async def test_unpair(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test unpairing from device."""
        device, manager = device_with_manager
        manager.paired = True

        await device.unpair()

        assert manager.paired is False

    @pytest.mark.asyncio
    async def test_read_rssi(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test reading RSSI value."""
        device, manager = device_with_manager
        manager.rssi_return = -72

        rssi = await device.read_rssi()

        assert rssi == -72

    def test_set_disconnected_callback(self, device_with_manager: tuple[Device, AsyncMockConnectionManager]) -> None:
        """Test setting disconnected callback."""
        device, manager = device_with_manager
        callback_called = []

        def on_disconnect() -> None:
            callback_called.append(True)

        device.set_disconnected_callback(on_disconnect)

        # Verify callback was passed to manager
        assert manager.disconnected_callback is not None

    @pytest.mark.asyncio
    async def test_read_descriptor_by_uuid(
        self, device_with_manager: tuple[Device, AsyncMockConnectionManager]
    ) -> None:
        """Test reading descriptor by UUID."""
        device, _ = device_with_manager
        cccd_uuid = BluetoothUUID(0x2902)

        result = await device.read_descriptor(cccd_uuid)

        assert result is not None

    @pytest.mark.asyncio
    async def test_write_descriptor_by_uuid(
        self, device_with_manager: tuple[Device, AsyncMockConnectionManager]
    ) -> None:
        """Test writing descriptor by UUID."""
        device, _ = device_with_manager
        cccd_uuid = BluetoothUUID(0x2902)
        enable_notifications = b"\x01\x00"

        await device.write_descriptor(cccd_uuid, enable_notifications)

        # Should not raise

    @pytest.mark.asyncio
    async def test_write_descriptor_with_instance(
        self, device_with_manager: tuple[Device, AsyncMockConnectionManager]
    ) -> None:
        """Test writing descriptor using descriptor instance."""
        device, _ = device_with_manager
        cccd = CCCDDescriptor()
        enable_notifications = b"\x01\x00"

        await device.write_descriptor(cccd, enable_notifications)

        # Should extract UUID from descriptor instance
