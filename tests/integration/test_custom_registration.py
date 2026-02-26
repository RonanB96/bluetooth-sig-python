"""Tests for runtime custom characteristic and service registration."""

from __future__ import annotations

from types import new_class
from typing import Any

import pytest

from bluetooth_sig.core.translator import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.gatt.characteristics.utils import DataParser
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.services.custom import CustomBaseGattService
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types import CharacteristicInfo, ServiceInfo
from bluetooth_sig.types.gatt_enums import GattProperty
from bluetooth_sig.types.uuid import BluetoothUUID


class CustomCharacteristicImpl(CustomBaseCharacteristic):
    """Test custom characteristic implementation."""

    # Progressive API Level 2: _info class attribute (auto-handled via __init_subclass__)
    _info = CharacteristicInfo(
        uuid=BluetoothUUID("abcd1234-0000-1000-8000-00805f9b34fb"),
        name="CustomCharacteristicImpl",
        unit="",
        python_type=int,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True) -> int:
        """Parse test data as uint16."""
        return DataParser.parse_int16(bytes(data), 0, signed=False)

    def _encode_value(self, data: int) -> bytearray:
        """Encode value to bytes (required abstract method)."""
        return bytearray(data.to_bytes(2, "little", signed=False))

    @classmethod
    def from_uuid(
        cls, uuid: str | BluetoothUUID, _properties: set[GattProperty] | None = None
    ) -> CustomCharacteristicImpl:
        """Create instance from UUID for registry compatibility (legacy support)."""
        if isinstance(uuid, str):
            uuid = BluetoothUUID(uuid)

        info = CharacteristicInfo(
            uuid=uuid,
            name="CustomCharacteristicImpl",
            unit="",
            python_type=int,
        )

        return cls(info=info)


class CustomServiceImpl(CustomBaseGattService):
    """Test custom service implementation."""

    _service_name = "Test Service"


class TestRuntimeRegistration:
    """Test runtime registration functionality."""

    @pytest.fixture(autouse=True)
    def _reset_registries(self, reset_registries: None) -> None:
        """Automatically reset registries after each test in this class."""

    def test_register_custom_characteristic_metadata(self) -> None:
        """Test registering custom characteristic metadata."""
        uuid_registry.register_characteristic(
            uuid=BluetoothUUID("abcd1234-0000-1000-8000-00805f9b34fb"),
            name="Test Characteristic",
            unit="°C",
            python_type=float,
        )

        # Verify registration
        info = uuid_registry.get_characteristic_info("abcd1234-0000-1000-8000-00805f9b34fb")
        assert info is not None
        assert info.name == "Test Characteristic"
        assert info.unit == "°C"
        assert info.python_type is float

    def test_register_custom_service_metadata(self) -> None:
        """Test registering custom service metadata."""
        uuid_registry.register_service(
            uuid=BluetoothUUID("12345678-1234-1234-1234-123456789abc"),
            name="Test Service",
        )

        # Verify registration
        info = uuid_registry.get_service_info("12345678-1234-1234-1234-123456789abc")
        assert info is not None
        assert info.name == "Test Service"

    def test_register_characteristic_class(self) -> None:
        """Test registering a custom characteristic class."""
        CharacteristicRegistry.register_characteristic_class(
            "abcd1234-0000-1000-8000-00805f9b34fb", CustomCharacteristicImpl
        )

        # Verify registration
        cls = CharacteristicRegistry.get_characteristic_class_by_uuid("abcd1234-0000-1000-8000-00805f9b34fb")
        assert cls == CustomCharacteristicImpl

    def test_register_service_class(self) -> None:
        """Test registering a custom service class."""
        GattServiceRegistry.register_service_class("12345678-1234-1234-1234-123456789abc", CustomServiceImpl)

        # Verify registration
        cls = GattServiceRegistry.get_service_class("12345678-1234-1234-1234-123456789abc")
        assert cls == CustomServiceImpl

    def test_translator_register_custom_characteristic(self) -> None:
        """Test translator convenience method for registering custom characteristic."""
        translator = BluetoothSIGTranslator()

        translator.register_custom_characteristic_class(
            "abcd1234-0000-1000-8000-00805f9b34fb",
            CustomCharacteristicImpl,
            info=CharacteristicInfo(
                uuid=BluetoothUUID("abcd1234-0000-1000-8000-00805f9b34fb"),
                name="Test Characteristic",
                unit="°C",
                python_type=int,
            ),
        )  # Verify class registration
        cls = CharacteristicRegistry.get_characteristic_class_by_uuid("abcd1234-0000-1000-8000-00805f9b34fb")
        assert cls == CustomCharacteristicImpl

        # Verify metadata registration
        info = uuid_registry.get_characteristic_info("abcd1234-0000-1000-8000-00805f9b34fb")
        assert info is not None
        assert info.name == "Test Characteristic"
        assert info.unit == "°C"

    def test_translator_register_custom_service(self) -> None:
        """Test translator convenience method for registering custom service."""
        translator = BluetoothSIGTranslator()

        translator.register_custom_service_class(
            "12345678-1234-1234-1234-123456789abc",
            CustomServiceImpl,
            info=ServiceInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789abc"),
                name="Test Service",
            ),
        )

        # Verify class registration
        cls = GattServiceRegistry.get_service_class("12345678-1234-1234-1234-123456789abc")
        assert cls == CustomServiceImpl

        # Verify metadata registration
        info = uuid_registry.get_service_info("12345678-1234-1234-1234-123456789abc")
        assert info is not None
        assert info.name == "Test Service"

    def test_parse_custom_characteristic(self) -> None:
        """Test parsing data with a custom characteristic."""
        translator = BluetoothSIGTranslator()

        # Register custom characteristic
        translator.register_custom_characteristic_class(
            "abcd1234-0000-1000-8000-00805f9b34fb", CustomCharacteristicImpl
        )

        # Parse data
        test_data = bytes([0x34, 0x12])  # 0x1234 = 4660
        result = translator.parse_characteristic("abcd1234-0000-1000-8000-00805f9b34fb", test_data)

        assert result == 4660

    def test_conflict_detection(self) -> None:
        """Test that conflicts with SIG entries are detected."""
        # Try to register a known SIG UUID without override
        with pytest.raises(ValueError, match="conflicts with existing SIG"):
            uuid_registry.register_characteristic(
                uuid=BluetoothUUID("2A19"),  # Battery Level UUID
                name="Custom Battery",
                unit="%",
                python_type=int,
            )

    def test_override_allowed(self) -> None:
        """Test that override=True allows replacing SIG entries."""
        # Should not raise with override=True
        uuid_registry.register_characteristic(
            uuid=BluetoothUUID("2A19"),  # Battery Level UUID
            name="Custom Battery",
            unit="%",
            python_type=int,
            override=True,
        )

        # Verify override worked
        info = uuid_registry.get_characteristic_info("2A19")
        assert info is not None
        assert info.name == "Custom Battery"

    def test_invalid_class_registration(self) -> None:
        """Test that invalid classes are rejected."""

        class InvalidCharacteristic:
            pass

        with pytest.raises(TypeError, match="must inherit from BaseCharacteristic"):
            CharacteristicRegistry.register_characteristic_class(
                "abcd1234-0000-1000-8000-00805f9b34fb",
                InvalidCharacteristic,  # type: ignore[arg-type]
            )

    def test_unregister_characteristic_class(self) -> None:
        """Test unregistering a custom characteristic class."""
        # Use a UUID that won't collide with built-ins
        test_uuid = "ffff1234-0000-1000-8000-00805f9b34fb"

        # Register first
        CharacteristicRegistry.register_characteristic_class(test_uuid, CustomCharacteristicImpl)

        # Verify registered
        cls = CharacteristicRegistry.get_characteristic_class_by_uuid(test_uuid)
        assert cls == CustomCharacteristicImpl

        # Unregister
        CharacteristicRegistry.unregister_characteristic_class(test_uuid)

        # Verify unregistered
        cls = CharacteristicRegistry.get_characteristic_class_by_uuid(test_uuid)
        assert cls is None

    def test_custom_base_classes(self) -> None:
        """Test that custom base classes have the _is_custom marker."""
        assert hasattr(CustomCharacteristicImpl, "_is_custom")
        assert CustomCharacteristicImpl._is_custom is True  # pylint: disable=protected-access

        assert hasattr(CustomServiceImpl, "_is_custom")
        assert CustomServiceImpl._is_custom is True  # pylint: disable=protected-access

    def test_sig_override_permission_required(self) -> None:
        """Test that SIG UUID override requires _allows_sig_override=True on the custom class."""
        # Attempt to define class with SIG UUID without _allows_sig_override should fail
        with pytest.raises(ValueError, match="SIG UUID.*without override flag"):

            def _class_body(namespace: dict[str, Any]) -> None:  # pragma: no cover
                namespace.update(
                    {
                        "__doc__": "Test class attempting SIG override without permission.",
                        "_info": CharacteristicInfo(
                            uuid=BluetoothUUID("2A19"),  # Battery Level UUID (SIG assigned)
                            name="Unauthorized SIG Override",
                            unit="%",
                            python_type=int,
                        ),
                    }
                )

                def _decode_value(  # pylint: disable=duplicate-code
                    # NOTE: Minimal characteristic implementation duplicates other test fixtures.
                    # Duplication justified because:
                    # 1. Test isolation - each test creates its own custom characteristic
                    # 2. Boilerplate decode/encode stubs required by CustomBaseCharacteristic API
                    # 3. Consolidation would reduce test independence and clarity
                    self: CustomBaseCharacteristic,
                    data: bytearray,
                    ctx: CharacteristicContext | None = None,
                ) -> int:
                    return data[0]

                def _encode_value(self: CustomBaseCharacteristic, data: int) -> bytearray:
                    return bytearray([data])

                namespace["_decode_value"] = _decode_value
                namespace["_encode_value"] = _encode_value

            new_class(
                "SIGOverrideWithoutPermission",
                (CustomBaseCharacteristic,),
                {"allow_sig_override": False},
                _class_body,
            )

    def test_sig_override_permission_allowed(self) -> None:
        """Test that SIG UUID override works when _allows_sig_override=True is set."""

        # Should not raise with allow_sig_override=True
        class SIGOverrideWithPermission(CustomBaseCharacteristic, allow_sig_override=True):
            """Test class with explicit SIG override permission."""

            _info = CharacteristicInfo(
                uuid=BluetoothUUID("2A19"),  # Battery Level UUID (SIG assigned)
                name="Authorized SIG Override",
                unit="%",
                python_type=int,
            )

            def _decode_value(  # pylint: disable=duplicate-code
                # NOTE: Minimal characteristic implementation duplicates other test fixtures.
                # Duplication justified because:
                # 1. Test isolation - each test creates its own custom characteristic
                # 2. Boilerplate decode/encode stubs required by CustomBaseCharacteristic API
                # 3. Consolidation would reduce test independence and clarity
                self,
                data: bytearray,
                ctx: CharacteristicContext | None = None,
                *,
                validate: bool = True,
            ) -> int:
                return data[0]

            def _encode_value(self, data: int) -> bytearray:
                return bytearray([data])

        # Should work without error
        char = SIGOverrideWithPermission()
        assert char.uuid == BluetoothUUID("2A19")
        assert char.get_allows_sig_override() is True

        # Should also work with registry registration
        CharacteristicRegistry.register_characteristic_class(
            "2A19",  # Battery Level UUID (SIG assigned)
            SIGOverrideWithPermission,
            override=True,
        )

        # Verify override worked
        cls = CharacteristicRegistry.get_characteristic_class_by_uuid("2A19")
        assert cls == SIGOverrideWithPermission
