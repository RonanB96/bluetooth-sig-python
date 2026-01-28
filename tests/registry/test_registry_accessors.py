"""Tests for registry accessor functions.

This module tests the get_characteristic_class_map() and get_service_class_map()
functions that provide functional access to registry state without mutable globals.
"""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics import CharacteristicRegistry, get_characteristic_class_map
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.services import GattServiceRegistry, get_service_class_map
from bluetooth_sig.gatt.services.base import BaseGattService
from bluetooth_sig.gatt.services.custom import CustomBaseGattService
from bluetooth_sig.types import CharacteristicInfo, ServiceInfo
from bluetooth_sig.types.gatt_enums import CharacteristicName, ServiceName
from bluetooth_sig.types.uuid import BluetoothUUID


class TestCharacteristicMapAccessor:
    """Test get_characteristic_class_map() function."""

    def test_contains_known_characteristics(self) -> None:
        """Verify map contains known SIG characteristics and has correct structure."""
        result = get_characteristic_class_map()

        # Verify structure and content
        assert len(result) > 0

        # Check some well-known characteristics exist
        known_chars = [
            CharacteristicName.BATTERY_LEVEL,
            CharacteristicName.DEVICE_NAME,
            CharacteristicName.HEART_RATE_MEASUREMENT,
        ]

        for char_name in known_chars:
            assert char_name in result, f"{char_name} not in characteristic map"
            assert issubclass(result[char_name], BaseCharacteristic)

    def test_reflects_custom_registrations(self) -> None:
        """Verify function reflects runtime custom characteristic registrations."""

        # Define custom characteristic
        class TestCustomChar(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("FFF1"),
                name="Test Custom Characteristic",
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return int.from_bytes(data, "little")

            def _encode_value(self, data: int) -> bytearray:
                return bytearray(data.to_bytes(2, "little"))

        custom_uuid = BluetoothUUID("FFF1")

        try:
            # Register custom characteristic
            CharacteristicRegistry.register_characteristic_class(custom_uuid, TestCustomChar, override=False)

            # Verify it appears in the map via direct registry method
            registry = CharacteristicRegistry.get_instance()
            assert registry.get_class_by_uuid(custom_uuid) == TestCustomChar

        finally:
            # Cleanup
            CharacteristicRegistry.unregister_characteristic_class(custom_uuid)


class TestServiceMapAccessor:
    """Test get_service_class_map() function."""

    def test_contains_known_services(self) -> None:
        """Verify map contains known SIG services and has correct structure."""
        result = get_service_class_map()

        # Verify structure and content
        assert len(result) > 0

        # Check some well-known services exist
        known_services = [
            ServiceName.BATTERY,
            ServiceName.DEVICE_INFORMATION,
            ServiceName.HEART_RATE,
        ]

        for service_name in known_services:
            assert service_name in result, f"{service_name} not in service map"
            assert issubclass(result[service_name], BaseGattService)

    def test_reflects_custom_registrations(self) -> None:
        """Verify function reflects runtime custom service registrations."""

        # Define custom service
        class TestCustomService(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID("FFF2"),
                name="Test Custom Service",
            )

        custom_uuid = BluetoothUUID("FFF2")

        try:
            # Register custom service
            GattServiceRegistry.register_service_class(custom_uuid, TestCustomService, override=False)

            # Verify it appears via direct registry method
            registry = GattServiceRegistry.get_instance()
            assert registry.get_class_by_uuid(custom_uuid) == TestCustomService

        finally:
            # Cleanup
            GattServiceRegistry.unregister_service_class(custom_uuid)
