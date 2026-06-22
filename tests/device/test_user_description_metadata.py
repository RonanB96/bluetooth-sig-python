"""Tests for User Description metadata on discovered characteristics."""

from __future__ import annotations

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.device import Device
from bluetooth_sig.device.connected import DeviceService
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.descriptors.characteristic_user_description import (
    CharacteristicUserDescriptionDescriptor,
)
from bluetooth_sig.gatt.services import BatteryService
from bluetooth_sig.types.uuid import BluetoothUUID
from tests.device.test_device_async_methods import AsyncMockClientManager


class UserDescriptionMockClient(AsyncMockClientManager):
    """Mock client returning User Description UTF-8 bytes."""

    async def read_gatt_descriptor(self, desc_uuid: BluetoothUUID) -> bytes:
        return b"Outdoor sensor"


@pytest.fixture
def device_with_battery() -> Device:
    """Device with battery service discovered and cached."""
    device = Device(UserDescriptionMockClient(), BluetoothSIGTranslator())
    battery = BatteryLevelCharacteristic()
    service_uuid = BatteryService.get_class_uuid()
    service = DeviceService(
        uuid=service_uuid,
        service_class=BatteryService,
        characteristics={str(battery.uuid): battery},
    )
    device.connected.services[str(service_uuid)] = service
    return device


class TestUserDescriptionMetadata:
    """User Description labels attach to characteristic metadata only."""

    @pytest.mark.asyncio
    async def test_read_descriptor_stores_user_description(self, device_with_battery: Device) -> None:
        """read_descriptor with characteristic_uuid caches parsed label."""
        battery_uuid = str(BatteryLevelCharacteristic.get_class_uuid())
        user_desc = CharacteristicUserDescriptionDescriptor()

        await device_with_battery.read_descriptor(user_desc, characteristic_uuid=battery_uuid)

        assert device_with_battery.get_user_description_for_characteristic(battery_uuid) == "Outdoor sensor"

    def test_attach_user_description_from_raw_bytes(self, device_with_battery: Device) -> None:
        """attach_user_description parses UTF-8 without a live descriptor read."""
        battery_uuid = str(BatteryLevelCharacteristic.get_class_uuid())
        label = device_with_battery.attach_user_description(battery_uuid, b"Indoor sensor")

        assert label == "Indoor sensor"
        assert device_with_battery.get_user_description_for_characteristic(battery_uuid) == "Indoor sensor"

    def test_get_user_description_missing_characteristic(self, device_with_battery: Device) -> None:
        """Unknown characteristic UUID returns None."""
        assert device_with_battery.get_user_description_for_characteristic("FFFF") is None
