"""Tests for peripheral device type definitions.

Tests for CharacteristicDefinition and ServiceDefinition dataclasses
used by PeripheralManagerProtocol implementations.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.peripheral_types import CharacteristicDefinition, ServiceDefinition
from bluetooth_sig.types.uuid import BluetoothUUID


class TestCharacteristicDefinition:
    """Tests for CharacteristicDefinition dataclass."""

    def test_creation_with_defaults(self) -> None:
        """Test creating CharacteristicDefinition with minimal arguments."""
        uuid = BluetoothUUID("2A19")
        char_def = CharacteristicDefinition(
            uuid=uuid,
            properties=GattProperty.READ,
        )

        assert char_def.uuid == uuid
        assert char_def.properties == GattProperty.READ
        assert char_def.initial_value == bytearray()
        assert char_def.readable is True
        assert char_def.writable is False
        assert char_def.on_read is None
        assert char_def.on_write is None

    def test_creation_with_all_fields(self) -> None:
        """Test creating CharacteristicDefinition with all fields populated."""
        uuid = BluetoothUUID("2A19")
        initial = bytearray(b"\x55")
        on_read = lambda: bytearray(b"\x60")  # noqa: E731
        on_write = lambda data: None  # noqa: E731

        char_def = CharacteristicDefinition(
            uuid=uuid,
            properties=GattProperty.READ | GattProperty.NOTIFY,
            initial_value=initial,
            readable=True,
            writable=False,
            on_read=on_read,
            on_write=on_write,
        )

        assert char_def.uuid == uuid
        assert char_def.properties == GattProperty.READ | GattProperty.NOTIFY
        assert char_def.initial_value == bytearray(b"\x55")
        assert char_def.readable is True
        assert char_def.writable is False
        assert char_def.on_read is on_read
        assert char_def.on_write is on_write

    def test_from_characteristic_success(self) -> None:
        """Test factory method with a real SIG characteristic."""
        char = BatteryLevelCharacteristic()
        char_def = CharacteristicDefinition.from_characteristic(char, 85)

        assert char_def.uuid == BluetoothUUID("2A19")
        assert char_def.initial_value == bytearray(b"\x55")
        assert char_def.properties == GattProperty.READ | GattProperty.NOTIFY
        assert char_def.readable is True
        assert char_def.writable is False

    def test_from_characteristic_with_custom_properties(self) -> None:
        """Test factory method with explicit properties override."""
        char = BatteryLevelCharacteristic()
        char_def = CharacteristicDefinition.from_characteristic(
            char,
            50,
            properties=GattProperty.READ | GattProperty.WRITE,
        )

        assert char_def.properties == GattProperty.READ | GattProperty.WRITE
        assert char_def.readable is True
        assert char_def.writable is True

    def test_from_characteristic_invalid_value(self) -> None:
        """Test factory method rejects values the characteristic cannot encode."""
        char = BatteryLevelCharacteristic()
        with pytest.raises(CharacteristicEncodeError):
            CharacteristicDefinition.from_characteristic(char, "not_a_number")

    def test_from_characteristic_out_of_range(self) -> None:
        """Test factory method with value outside characteristic range."""
        char = BatteryLevelCharacteristic()
        with pytest.raises(CharacteristicEncodeError):
            CharacteristicDefinition.from_characteristic(char, 999)

    def test_from_characteristic_with_callbacks(self) -> None:
        """Test factory method with read/write callbacks."""
        char = BatteryLevelCharacteristic()
        on_read = lambda: bytearray(b"\x32")  # noqa: E731
        on_write = lambda data: None  # noqa: E731

        char_def = CharacteristicDefinition.from_characteristic(
            char,
            50,
            on_read=on_read,
            on_write=on_write,
        )

        assert char_def.on_read is on_read
        assert char_def.on_write is on_write


class TestServiceDefinition:
    """Tests for ServiceDefinition dataclass."""

    def test_creation_with_defaults(self) -> None:
        """Test creating ServiceDefinition with minimal arguments."""
        uuid = BluetoothUUID("180F")
        service = ServiceDefinition(uuid=uuid)

        assert service.uuid == uuid
        assert service.characteristics == []
        assert service.primary is True

    def test_creation_with_characteristics(self) -> None:
        """Test creating ServiceDefinition with characteristics list."""
        service_uuid = BluetoothUUID("180F")
        char_def = CharacteristicDefinition(
            uuid=BluetoothUUID("2A19"),
            properties=GattProperty.READ | GattProperty.NOTIFY,
            initial_value=bytearray(b"\x55"),
        )

        service = ServiceDefinition(
            uuid=service_uuid,
            characteristics=[char_def],
        )

        assert service.uuid == service_uuid
        assert len(service.characteristics) == 1
        assert service.characteristics[0].uuid == BluetoothUUID("2A19")
        assert service.primary is True

    def test_creation_secondary_service(self) -> None:
        """Test creating a secondary (non-primary) service."""
        service = ServiceDefinition(
            uuid=BluetoothUUID("180F"),
            primary=False,
        )

        assert service.primary is False

    def test_creation_with_multiple_characteristics(self) -> None:
        """Test service with multiple characteristics."""
        char1 = CharacteristicDefinition(
            uuid=BluetoothUUID("2A6E"),
            properties=GattProperty.READ | GattProperty.NOTIFY,
        )
        char2 = CharacteristicDefinition(
            uuid=BluetoothUUID("2A6F"),
            properties=GattProperty.READ | GattProperty.NOTIFY,
        )

        service = ServiceDefinition(
            uuid=BluetoothUUID("181A"),
            characteristics=[char1, char2],
        )

        assert len(service.characteristics) == 2
        assert service.characteristics[0].uuid == BluetoothUUID("2A6E")
        assert service.characteristics[1].uuid == BluetoothUUID("2A6F")

    def test_empty_characteristics_list_is_mutable(self) -> None:
        """Test that the default characteristics list allows mutation."""
        service = ServiceDefinition(uuid=BluetoothUUID("180F"))

        char_def = CharacteristicDefinition(
            uuid=BluetoothUUID("2A19"),
            properties=GattProperty.READ,
        )
        service.characteristics.append(char_def)

        assert len(service.characteristics) == 1

    def test_separate_instances_have_independent_lists(self) -> None:
        """Test that separate ServiceDefinition instances don't share lists."""
        service1 = ServiceDefinition(uuid=BluetoothUUID("180F"))
        service2 = ServiceDefinition(uuid=BluetoothUUID("181A"))

        service1.characteristics.append(
            CharacteristicDefinition(
                uuid=BluetoothUUID("2A19"),
                properties=GattProperty.READ,
            )
        )

        assert len(service1.characteristics) == 1
        assert len(service2.characteristics) == 0
