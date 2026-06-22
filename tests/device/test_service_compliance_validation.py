"""Tests for opt-in GATT service compliance validation after discovery."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.device.client import ClientManagerProtocol
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.services import BatteryService, ServiceHealthStatus
from bluetooth_sig.gatt.services.base import ServiceValidationResult
from bluetooth_sig.types.advertising.ad_structures import AdvertisingDataStructures, CoreAdvertisingData
from bluetooth_sig.types.advertising.result import AdvertisementData
from bluetooth_sig.types.device_types import DeviceService as ClientDeviceService
from bluetooth_sig.types.uuid import BluetoothUUID


class ValidationMockClientManager(ClientManagerProtocol):
    """Mock connection manager for service validation tests."""

    def __init__(self, address: str = "AA:BB:CC:DD:EE:FF", **kwargs: object) -> None:
        super().__init__(address, **kwargs)
        self._connected = True
        self._services: list[ClientDeviceService] = []

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def mtu_size(self) -> int:
        return 247

    @property
    def name(self) -> str:
        return "Validation Mock Device"

    async def connect(self, *, timeout: float = 10.0) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def read_gatt_char(self, char_uuid: BluetoothUUID) -> bytes:
        return b"\x64"

    async def write_gatt_char(self, char_uuid: BluetoothUUID, data: bytes, response: bool = True) -> None:
        pass

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        return b""

    async def write_gatt_descriptor(self, desc_uuid: BluetoothUUID, data: bytes) -> None:
        pass

    async def get_services(self) -> list[ClientDeviceService]:
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
def validation_device() -> tuple[Device, ValidationMockClientManager]:
    """Device with mock manager for validation tests."""
    manager = ValidationMockClientManager()
    device = Device(manager, BluetoothSIGTranslator())
    return device, manager


class TestValidateDiscoveredServices:
    """Tests for Device.validate_discovered_services()."""

    @pytest.mark.asyncio
    async def test_compliant_battery_service(
        self, validation_device: tuple[Device, ValidationMockClientManager]
    ) -> None:
        """Battery Service with required Battery Level characteristic is healthy."""
        device, manager = validation_device
        battery_char = BatteryLevelCharacteristic()
        manager._services = [
            ClientDeviceService(
                service=BatteryService(),
                characteristics={str(battery_char.uuid): battery_char},
            )
        ]

        await device.discover_services()
        results = device.validate_discovered_services()

        assert len(results) == 1
        assert results[0].service_uuid.short_form == "180F"
        assert results[0].service_name == "Battery"
        assert results[0].validation.status == ServiceHealthStatus.COMPLETE
        assert results[0].validation.is_healthy is True
        assert results[0].validation.missing_required == []

    @pytest.mark.asyncio
    async def test_non_compliant_battery_service_missing_level(
        self, validation_device: tuple[Device, ValidationMockClientManager]
    ) -> None:
        """Battery Service without Battery Level is reported as incomplete."""
        device, manager = validation_device
        manager._services = [ClientDeviceService(service=BatteryService(), characteristics={})]

        await device.discover_services()
        results = device.validate_discovered_services()

        assert len(results) == 1
        assert results[0].validation.status == ServiceHealthStatus.INCOMPLETE
        assert results[0].validation.is_healthy is False
        assert results[0].validation.has_errors is True
        battery_level_missing = any(char.name == "Battery Level" for char in results[0].validation.missing_required)
        assert battery_level_missing

    @pytest.mark.asyncio
    async def test_empty_discovery_returns_empty_results(
        self, validation_device: tuple[Device, ValidationMockClientManager]
    ) -> None:
        """No discovered services yields an empty validation list."""
        device, manager = validation_device
        manager._services = []

        await device.discover_services()
        results = device.validate_discovered_services()

        assert results == []

    def test_validate_device_services_unit(self) -> None:
        """validate_device_services helper validates without a Device instance."""
        from bluetooth_sig.device.connected import DeviceService
        from bluetooth_sig.device.validation import validate_device_services

        battery_char = BatteryLevelCharacteristic()
        device_service = DeviceService(
            uuid=BatteryService.get_class_uuid(),
            service_class=BatteryService,
            characteristics={str(battery_char.uuid): battery_char},
        )
        results = validate_device_services({str(device_service.uuid): device_service})

        assert len(results) == 1
        assert isinstance(results[0].validation, ServiceValidationResult)
        assert results[0].validation.is_healthy is True
