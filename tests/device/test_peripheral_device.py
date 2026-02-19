"""Tests for PeripheralDevice high-level GATT server abstraction.

Validates the composition of PeripheralManagerProtocol + BaseCharacteristic
encoding, lifecycle management, value updates, and fluent configuration.
"""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.device.peripheral import PeripheralManagerProtocol
from bluetooth_sig.device.peripheral_device import HostedCharacteristic, PeripheralDevice
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.types.peripheral_types import CharacteristicDefinition, ServiceDefinition
from bluetooth_sig.types.uuid import BluetoothUUID


# ---------------------------------------------------------------------------
# Mock backend
# ---------------------------------------------------------------------------


class MockPeripheralManager(PeripheralManagerProtocol):
    """In-memory mock of PeripheralManagerProtocol for testing.

    Tracks all calls for assertion and simulates the advertising lifecycle.
    """

    def __init__(self, name: str = "MockPeripheral") -> None:
        super().__init__(name)
        self._advertising = False
        self._characteristic_values: dict[str, bytearray] = {}
        self._notify_log: list[tuple[str, bytearray, bool]] = []

    async def start(self) -> None:
        if not self._services:
            raise RuntimeError("No services registered")
        self._advertising = True

    async def stop(self) -> None:
        self._advertising = False

    @property
    def is_advertising(self) -> bool:
        return self._advertising

    async def update_characteristic(
        self,
        char_uuid: str | BluetoothUUID,
        value: bytearray,
        *,
        notify: bool = True,
    ) -> None:
        uuid_str = str(char_uuid).upper()
        if not self._advertising:
            raise RuntimeError("Peripheral not started")
        self._characteristic_values[uuid_str] = value
        self._notify_log.append((uuid_str, value, notify))

    async def get_characteristic_value(self, char_uuid: str | BluetoothUUID) -> bytearray:
        uuid_str = str(char_uuid).upper()
        if uuid_str not in self._characteristic_values:
            raise KeyError(f"Characteristic {uuid_str} not found")
        return self._characteristic_values[uuid_str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BATTERY_SERVICE_UUID = "180F"
BATTERY_CHAR_UUID = "00002A19-0000-1000-8000-00805F9B34FB"


def _make_device(name: str = "TestDevice") -> tuple[PeripheralDevice, MockPeripheralManager]:
    """Create a PeripheralDevice with a mock backend."""
    backend = MockPeripheralManager(name)
    device = PeripheralDevice(backend)
    return device, backend


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPeripheralDeviceInit:
    """Constructor and basic properties."""

    def test_init_sets_name(self) -> None:
        device, _ = _make_device("Sensor-1")
        assert device.name == "Sensor-1"

    def test_init_not_advertising(self) -> None:
        device, _ = _make_device()
        assert device.is_advertising is False

    def test_init_no_services(self) -> None:
        device, _ = _make_device()
        assert device.services == []

    def test_init_no_hosted_characteristics(self) -> None:
        device, _ = _make_device()
        assert device.hosted_characteristics == {}

    def test_repr_stopped(self) -> None:
        device, _ = _make_device("Demo")
        r = repr(device)
        assert "Demo" in r
        assert "stopped" in r


class TestAddCharacteristic:
    """Registration of characteristics via the typed helper."""

    def test_add_characteristic_returns_definition(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        char_def = device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=85,
        )

        assert isinstance(char_def, CharacteristicDefinition)
        assert char_def.initial_value == bytearray(b"\x55")  # 85 decimal

    def test_add_characteristic_creates_hosted_entry(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )

        hosted = device.hosted_characteristics
        assert BATTERY_CHAR_UUID in hosted
        assert isinstance(hosted[BATTERY_CHAR_UUID], HostedCharacteristic)
        assert hosted[BATTERY_CHAR_UUID].last_value == 50

    def test_add_characteristic_creates_pending_service(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=75,
        )

        # Pending services are flushed on start(); backend has none yet
        assert device.services == []

    def test_add_characteristic_after_start_raises(self) -> None:
        """Cannot add characteristics once advertising has started."""
        device, backend = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=99,
        )

        # Force-start so is_advertising returns True
        backend._advertising = True

        with pytest.raises(RuntimeError, match="Cannot add characteristics"):
            device.add_characteristic(
                service_uuid=BATTERY_SERVICE_UUID,
                characteristic=BatteryLevelCharacteristic(),
                initial_value=10,
            )


class TestLifecycle:
    """Start / stop lifecycle."""

    @pytest.mark.asyncio
    async def test_start_flushes_pending_services(self) -> None:
        device, backend = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=90,
        )

        await device.start()

        assert device.is_advertising is True
        assert len(backend.services) == 1
        assert str(backend.services[0].uuid).upper().startswith("0000180F")

    @pytest.mark.asyncio
    async def test_stop_clears_advertising(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=80,
        )

        await device.start()
        assert device.is_advertising is True

        await device.stop()
        assert device.is_advertising is False

    @pytest.mark.asyncio
    async def test_repr_advertising(self) -> None:
        device, _ = _make_device("Live")
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=60,
        )
        await device.start()

        r = repr(device)
        assert "advertising" in r
        assert "Live" in r


class TestUpdateValue:
    """Typed value encoding and push to backend."""

    @pytest.mark.asyncio
    async def test_update_value_encodes_and_pushes(self) -> None:
        device, backend = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )
        await device.start()

        await device.update_value(char, 72)

        # Verify backend received the encoded bytes
        assert len(backend._notify_log) == 1
        uuid_sent, value_sent, notify_flag = backend._notify_log[0]
        assert uuid_sent == BATTERY_CHAR_UUID
        assert value_sent == bytearray(b"\x48")  # 72 decimal
        assert notify_flag is True

    @pytest.mark.asyncio
    async def test_update_value_by_uuid_string(self) -> None:
        device, backend = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )
        await device.start()

        # Pass UUID string instead of characteristic instance
        await device.update_value(BATTERY_CHAR_UUID, 33)

        _, value_sent, _ = backend._notify_log[0]
        assert value_sent == bytearray(b"\x21")  # 33 decimal

    @pytest.mark.asyncio
    async def test_update_value_without_notify(self) -> None:
        device, backend = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )
        await device.start()

        await device.update_value(char, 10, notify=False)

        _, _, notify_flag = backend._notify_log[0]
        assert notify_flag is False

    @pytest.mark.asyncio
    async def test_update_value_unknown_uuid_raises(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )
        await device.start()

        with pytest.raises(KeyError, match="not hosted"):
            await device.update_value("FFFF", 42)

    @pytest.mark.asyncio
    async def test_update_value_updates_last_value(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )
        await device.start()

        await device.update_value(char, 72)

        hosted = device.hosted_characteristics[BATTERY_CHAR_UUID]
        assert hosted.last_value == 72


class TestUpdateRaw:
    """Pre-encoded byte push."""

    @pytest.mark.asyncio
    async def test_update_raw_pushes_bytes(self) -> None:
        device, backend = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=50,
        )
        await device.start()

        await device.update_raw("2A19", bytearray(b"\x63"))

        _, value_sent, _ = backend._notify_log[0]
        assert value_sent == bytearray(b"\x63")


class TestGetCurrentValue:
    """Reading back the last Python value."""

    @pytest.mark.asyncio
    async def test_get_current_value_initial(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=42,
        )

        value = await device.get_current_value(char)
        assert value == 42

    @pytest.mark.asyncio
    async def test_get_current_value_after_update(self) -> None:
        device, _ = _make_device()
        char = BatteryLevelCharacteristic()
        device.add_characteristic(
            service_uuid=BATTERY_SERVICE_UUID,
            characteristic=char,
            initial_value=42,
        )
        await device.start()

        await device.update_value(char, 99)
        value = await device.get_current_value(char)
        assert value == 99

    @pytest.mark.asyncio
    async def test_get_current_value_unknown_uuid_raises(self) -> None:
        device, _ = _make_device()

        with pytest.raises(KeyError, match="not hosted"):
            await device.get_current_value("DEAD")


class TestFluentConfiguration:
    """Fluent builder delegation to the backend."""

    def test_with_manufacturer_data_returns_self(self) -> None:
        device, _ = _make_device()
        result = device.with_manufacturer_data(0x004C, b"\x02\x15")
        assert result is device

    def test_with_manufacturer_data_delegates(self) -> None:
        device, backend = _make_device()
        device.with_manufacturer_data(0x004C, b"\x02\x15")
        assert backend.manufacturer_data is not None
        assert backend.manufacturer_data.company.id == 0x004C

    def test_with_tx_power_returns_self(self) -> None:
        device, _ = _make_device()
        result = device.with_tx_power(-10)
        assert result is device

    def test_with_tx_power_delegates(self) -> None:
        device, backend = _make_device()
        device.with_tx_power(-20)
        assert backend.tx_power == -20

    def test_with_connectable_delegates(self) -> None:
        device, backend = _make_device()
        device.with_connectable(False)
        assert backend.is_connectable_config is False

    def test_with_discoverable_delegates(self) -> None:
        device, backend = _make_device()
        device.with_discoverable(False)
        assert backend.is_discoverable_config is False

    def test_chaining(self) -> None:
        device, backend = _make_device()
        result = (
            device
            .with_tx_power(-5)
            .with_connectable(True)
            .with_discoverable(False)
        )
        assert result is device
        assert backend.tx_power == -5
        assert backend.is_connectable_config is True
        assert backend.is_discoverable_config is False


class TestAddService:
    """Direct ServiceDefinition registration."""

    @pytest.mark.asyncio
    async def test_add_service_delegates_to_backend(self) -> None:
        device, backend = _make_device()
        svc = ServiceDefinition(uuid=BluetoothUUID("180F"))
        await device.add_service(svc)

        assert len(backend.services) == 1
        assert str(backend.services[0].uuid) == str(BluetoothUUID("180F"))
