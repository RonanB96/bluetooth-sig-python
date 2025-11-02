"""Comprehensive tests for CustomBaseGattService library functionality.

This test suite focuses on testing the ACTUAL LIBRARY CODE for custom services:
- __init_subclass__ validation and SIG UUID protection
- __post_init__ and _info resolution mechanisms
- process_characteristics() method and characteristic discovery
- Integration with CharacteristicRegistry
- UnknownService creation and usage
- service_characteristics class variable usage
- Error handling and validation
- Info property access and override behavior
"""

from __future__ import annotations

from collections.abc import Callable
from types import new_class
from typing import Any

import pytest

from bluetooth_sig.core.translator import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.base import UnknownCharacteristic
from bluetooth_sig.gatt.services.base import BaseGattService, CustomBaseGattService, UnknownService
from bluetooth_sig.gatt.services.registry import GattServiceRegistry
from bluetooth_sig.types import CharacteristicInfo, ServiceInfo, ServiceRegistration
from bluetooth_sig.types.gatt_enums import GattProperty, ValueType
from bluetooth_sig.types.uuid import BluetoothUUID

# ==============================================================================
# Fixtures and Test Utilities
# ==============================================================================


@pytest.fixture
def service_class_factory() -> Callable[..., type[CustomBaseGattService]]:
    """Factory fixture to create custom service classes with unique UUIDs."""
    counter = 0

    def _create_service_class(
        uuid_base: str = "AA00",
        name: str = "Test Service",
        description: str = "Test",
        allow_sig_override: bool = False,
    ) -> type[CustomBaseGattService]:
        """Create a custom service class with a unique UUID.

        Args:
            uuid_base: First 4 chars of UUID (default: "AA00")
            name: Service name
            description: Service description
            allow_sig_override: Whether to allow SIG UUID override

        Returns:
            A new CustomBaseGattService subclass

        """
        nonlocal counter
        counter += 1

        # Generate unique UUID using counter
        uuid_str = f"{uuid_base}{counter:04X}-0000-1000-8000-00805F9B34FB"

        if allow_sig_override:

            class TestServiceWithOverride(CustomBaseGattService, allow_sig_override=True):
                _info = ServiceInfo(
                    uuid=BluetoothUUID(uuid_str),
                    name=name,
                    description=description,
                )

            return TestServiceWithOverride

        class TestService(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID(uuid_str),
                name=name,
                description=description,
            )

        return TestService

    return _create_service_class


# ==============================================================================
# Test: __init_subclass__ Validation
# ==============================================================================


class TestInitSubclassValidation:
    """Test __init_subclass__ SIG UUID validation."""

    def test_custom_uuid_allowed_without_override(self) -> None:
        """Test that custom (non-SIG) UUIDs work without override flag."""

        class CustomUUIDService(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID("AA000001-0000-1000-8000-00805F9B34FB"),
                name="Custom Service",
                description="Uses custom UUID",
            )

        # Should create without error
        service = CustomUUIDService()
        assert service.uuid == BluetoothUUID("AA000001-0000-1000-8000-00805F9B34FB")

    def test_sig_uuid_requires_override_flag(self) -> None:
        """Test that SIG UUIDs require allow_sig_override=True."""
        with pytest.raises(ValueError, match="without override flag"):

            def _service_body(namespace: dict[str, Any]) -> None:  # pragma: no cover
                namespace["_info"] = ServiceInfo(
                    uuid=BluetoothUUID("180F"),  # Battery Service (SIG)
                    name="Unauthorized",
                    description="Should fail",
                )

            new_class(
                "UnauthorizedSIGService",
                (CustomBaseGattService,),
                {"allow_sig_override": False},
                _service_body,
            )

    def test_sig_uuid_with_override_flag_succeeds(self) -> None:
        """Test that SIG UUIDs work with allow_sig_override=True."""

        class AuthorizedSIGService(CustomBaseGattService, allow_sig_override=True):
            _info = ServiceInfo(
                uuid=BluetoothUUID("180A"),  # Device Information (SIG)
                name="Authorized Override",
                description="Should work",
            )

        service = AuthorizedSIGService()
        assert service.info.uuid == BluetoothUUID("180A")
        # pylint: disable=protected-access
        assert service._allows_sig_override is True  # type: ignore[attr-defined]

    def test_configured_info_stored_in_class(self) -> None:
        """Test that _info is stored in _configured_info during __init_subclass__."""

        class ServiceWithInfo(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID("BB000001-0000-1000-8000-00805F9B34FB"),
                name="Test Service",
                description="Test",
            )

        # pylint: disable=protected-access
        # Testing internal state
        assert ServiceWithInfo._configured_info is not None  # type: ignore[attr-defined]
        assert ServiceWithInfo._configured_info.uuid == BluetoothUUID("BB000001-0000-1000-8000-00805F9B34FB")  # type: ignore[attr-defined, union-attr]


# ==============================================================================
# Test: __init__ and __post_init__ Behavior
# ==============================================================================


class TestInitAndPostInit:
    """Test __init__ and __post_init__ info resolution."""

    def test_info_from_class_attribute(self, service_class_factory: Callable[..., type[CustomBaseGattService]]) -> None:
        """Test that _info class attribute is used automatically."""
        service_cls = service_class_factory(name="Auto Info", description="Automatic info binding")
        service = service_cls()

        assert service.name == "Auto Info"
        assert service.summary == "Automatic info binding"
        assert isinstance(service.uuid, BluetoothUUID)

    def test_info_parameter_overrides_class_attribute(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that info parameter overrides _info class attribute."""
        service_cls = service_class_factory(name="Original", description="Original description")

        override_info = ServiceInfo(
            uuid=BluetoothUUID("EE000001-0000-1000-8000-00805F9B34FB"),
            name="Override",
            description="Overridden description",
        )

        service = service_cls(info=override_info)

        assert service.uuid == BluetoothUUID("EE000001-0000-1000-8000-00805F9B34FB")
        assert service.name == "Override"
        assert service.summary == "Overridden description"

    def test_missing_info_raises_error(self) -> None:
        """Test that missing _info and no parameter raises ValueError."""
        with pytest.raises(ValueError, match="requires either 'info' parameter or '_info' class attribute"):

            class NoInfoService(CustomBaseGattService):
                pass

            NoInfoService()

    def test_post_init_uses_provided_info(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that __post_init__ correctly uses provided info."""
        service_cls = service_class_factory()

        manual_info = ServiceInfo(
            uuid=BluetoothUUID("FF000002-0000-1000-8000-00805F9B34FB"),
            name="Manual",
            description="Manual info",
        )

        service = service_cls(info=manual_info)

        # Verify __post_init__ used the manual info, not class _info
        # pylint: disable=protected-access
        assert service._info == manual_info  # type: ignore[attr-defined]
        assert service.uuid == manual_info.uuid


# ==============================================================================
# Test: process_characteristics() Method
# ==============================================================================


class TestProcessCharacteristics:
    """Test process_characteristics() method functionality."""

    def test_process_empty_characteristics(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test processing empty characteristics dict."""
        service = service_class_factory()()
        service.process_characteristics({})

        assert len(service.characteristics) == 0

    def test_process_single_characteristic(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test processing a single discovered characteristic."""
        service = service_class_factory()()
        uuid = BluetoothUUID("12345678-0000-1000-8000-00805F9B34FB")
        discovered = {
            uuid: CharacteristicInfo(
                uuid=uuid,
                name="",
                properties=[GattProperty.READ, GattProperty.NOTIFY],
            ),
        }

        service.process_characteristics(discovered)

        assert len(service.characteristics) == 1
        assert uuid in service.characteristics

        # Verify it's an UnknownCharacteristic since UUID not in registry
        char = service.characteristics[uuid]
        assert isinstance(char, UnknownCharacteristic)

    def test_process_multiple_characteristics(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test processing multiple discovered characteristics."""
        service = service_class_factory()()
        uuid1 = BluetoothUUID("11111111-0000-1000-8000-00805F9B34FB")
        uuid2 = BluetoothUUID("22222222-0000-1000-8000-00805F9B34FB")
        uuid3 = BluetoothUUID("33333333-0000-1000-8000-00805F9B34FB")
        discovered = {
            uuid1: CharacteristicInfo(uuid=uuid1, name="", properties=[GattProperty.READ]),
            uuid2: CharacteristicInfo(uuid=uuid2, name="", properties=[GattProperty.WRITE]),
            uuid3: CharacteristicInfo(uuid=uuid3, name="", properties=[GattProperty.NOTIFY]),
        }

        service.process_characteristics(discovered)

        assert len(service.characteristics) == 3

    def test_process_sig_characteristic_uses_registry(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that SIG characteristics use CharacteristicRegistry."""
        service = service_class_factory()()

        # Battery Level is a known SIG characteristic
        uuid = BluetoothUUID("2A19")
        discovered = {
            uuid: CharacteristicInfo(
                uuid=uuid,
                name="Battery Level",
                properties=[GattProperty.READ, GattProperty.NOTIFY],
            ),
        }

        service.process_characteristics(discovered)

        assert len(service.characteristics) == 1
        assert uuid in service.characteristics

        # Should NOT be UnknownCharacteristic - should be from registry
        char = service.characteristics[uuid]
        # It will be a registered characteristic type, not Unknown
        assert char.info.name == "Battery Level"

    def test_process_characteristics_normalizes_uuid(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that UUID formats are normalized."""
        service = service_class_factory()()

        # Try different UUID formats
        short_uuid = BluetoothUUID("ABCD")
        long_uuid = BluetoothUUID("ABCDEF01-0000-1000-8000-00805F9B34FB")
        discovered = {
            short_uuid: CharacteristicInfo(uuid=short_uuid, name="", properties=[GattProperty.READ]),
            long_uuid: CharacteristicInfo(uuid=long_uuid, name="", properties=[GattProperty.WRITE]),
        }

        service.process_characteristics(discovered)

        assert len(service.characteristics) == 2

        # Verify both UUIDs are stored in normalized form
        assert short_uuid in service.characteristics
        assert long_uuid in service.characteristics

    def test_process_characteristics_extracts_properties(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that GATT properties are correctly extracted."""
        service = service_class_factory()()
        uuid = BluetoothUUID("AAAA0001-0000-1000-8000-00805F9B34FB")
        discovered = {
            uuid: CharacteristicInfo(
                uuid=uuid,
                name="",
                properties=[GattProperty.READ, GattProperty.WRITE, GattProperty.NOTIFY],
            ),
        }

        service.process_characteristics(discovered)
        char = service.characteristics[uuid]

        # Check that properties were extracted
        assert GattProperty.READ in char.info.properties
        assert GattProperty.WRITE in char.info.properties
        assert GattProperty.NOTIFY in char.info.properties


# ==============================================================================
# Test: UnknownService
# ==============================================================================


class TestUnknownService:
    """Test UnknownService class functionality."""

    def test_unknown_service_creation_with_uuid_only(self) -> None:
        """Test creating UnknownService with just UUID."""
        uuid = BluetoothUUID("FFFF0001-0000-1000-8000-00805F9B34FB")
        service = UnknownService(uuid=uuid)

        assert service.uuid == uuid
        assert "Unknown Service" in service.name
        assert str(uuid) in service.name

    def test_unknown_service_creation_with_custom_name(self) -> None:
        """Test creating UnknownService with custom name."""
        uuid = BluetoothUUID("FFFF0002-0000-1000-8000-00805F9B34FB")
        service = UnknownService(uuid=uuid, name="Custom Unknown Service")

        assert service.uuid == uuid
        assert service.name == "Custom Unknown Service"

    def test_unknown_service_process_characteristics(self) -> None:
        """Test that UnknownService can process characteristics."""
        uuid = BluetoothUUID("FFFF0003-0000-1000-8000-00805F9B34FB")
        service = UnknownService(uuid=uuid)

        uuid1 = BluetoothUUID("AAAA0001-0000-1000-8000-00805F9B34FB")
        uuid2 = BluetoothUUID("BBBB0001-0000-1000-8000-00805F9B34FB")
        discovered = {
            uuid1: CharacteristicInfo(uuid=uuid1, name="", properties=[GattProperty.READ]),
            uuid2: CharacteristicInfo(uuid=uuid2, name="", properties=[GattProperty.WRITE]),
        }

        service.process_characteristics(discovered)

        assert len(service.characteristics) == 2


# ==============================================================================
# Test: Service Registration
# ==============================================================================


class TestServiceRegistration:
    """Test runtime service registration."""

    def setup_method(self) -> None:
        """Clear registrations before each test."""
        GattServiceRegistry.clear_custom_registrations()

    def test_register_custom_service_class(self) -> None:
        """Test registering a custom service class."""

        class CustomService(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID("AA001000-0000-1000-8000-00805F9B34FB"),
                name="Custom",
                description="Custom service",
            )

        # pylint: disable=protected-access
        uuid_str = str(CustomService._configured_info.uuid)  # type: ignore[attr-defined,union-attr]
        GattServiceRegistry.register_service_class(uuid_str, CustomService)

        retrieved_cls = GattServiceRegistry.get_service_class(uuid_str)
        assert retrieved_cls == CustomService

    def test_unregister_custom_service_class(self) -> None:
        """Test unregistering a custom service class."""

        class CustomService(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID("AA001001-0000-1000-8000-00805F9B34FB"),
                name="Custom",
                description="Custom service",
            )

        # pylint: disable=protected-access
        uuid_str = str(CustomService._configured_info.uuid)  # type: ignore[attr-defined,union-attr]

        # Register
        GattServiceRegistry.register_service_class(uuid_str, CustomService)
        assert GattServiceRegistry.get_service_class(uuid_str) == CustomService

        # Unregister
        GattServiceRegistry.unregister_service_class(uuid_str)
        assert GattServiceRegistry.get_service_class(uuid_str) is None

    def test_register_via_translator(self) -> None:
        """Test registering service via BluetoothSIGTranslator."""

        class CustomService(CustomBaseGattService):
            _info = ServiceInfo(
                uuid=BluetoothUUID("AA001002-0000-1000-8000-00805F9B34FB"),
                name="Custom",
                description="Custom service",
            )

        translator = BluetoothSIGTranslator()
        service = CustomService()

        translator.register_custom_service_class(
            str(service.uuid),
            CustomService,
            metadata=ServiceRegistration(
                uuid=service.uuid,
                name="Custom",
                summary="Custom service",
            ),
        )

        retrieved_cls = GattServiceRegistry.get_service_class(str(service.uuid))
        assert retrieved_cls == CustomService

    def test_register_invalid_class_raises_error(self) -> None:
        """Test that registering non-service class raises TypeError."""

        class NotAService:
            pass

        with pytest.raises(TypeError, match="must inherit from BaseGattService"):
            GattServiceRegistry.register_service_class(
                "AA001003-0000-1000-8000-00805F9B34FB",
                NotAService,  # type: ignore[arg-type]
            )


# ==============================================================================
# Test: Info Property Access
# ==============================================================================


class TestInfoPropertyAccess:
    """Test service info property access."""

    def test_uuid_property(self, service_class_factory: Callable[..., type[CustomBaseGattService]]) -> None:
        """Test uuid property returns correct UUID."""
        service_cls = service_class_factory()
        service = service_cls()

        assert isinstance(service.uuid, BluetoothUUID)
        # Verify it matches the class's configured UUID
        # pylint: disable=protected-access
        assert service.uuid == service_cls._configured_info.uuid  # type: ignore[attr-defined,union-attr]

    def test_name_property(self, service_class_factory: Callable[..., type[CustomBaseGattService]]) -> None:
        """Test name property returns correct name."""
        service = service_class_factory(name="Test Service Name")()
        assert service.name == "Test Service Name"

    def test_summary_property(self, service_class_factory: Callable[..., type[CustomBaseGattService]]) -> None:
        """Test summary property returns description."""
        service = service_class_factory(description="Test description here")()
        assert service.summary == "Test description here"

    def test_info_property(self, service_class_factory: Callable[..., type[CustomBaseGattService]]) -> None:
        """Test info property returns ServiceInfo object."""
        service = service_class_factory()()
        info = service.info

        assert isinstance(info, ServiceInfo)
        assert info.uuid == service.uuid
        assert info.name == service.name
        assert info.description == service.summary


# ==============================================================================
# Test: Service Inheritance and Markers
# ==============================================================================


class TestServiceInheritance:
    """Test service inheritance and markers."""

    def test_custom_service_inherits_base_service(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that CustomBaseGattService inherits from BaseGattService."""
        service = service_class_factory()()

        assert isinstance(service, BaseGattService)
        assert isinstance(service, CustomBaseGattService)

    def test_custom_service_has_is_custom_marker(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that custom services have _is_custom = True."""
        service_cls = service_class_factory()
        service = service_cls()

        # pylint: disable=protected-access
        assert service_cls._is_custom is True  # type: ignore[attr-defined]
        assert service._is_custom is True  # type: ignore[attr-defined]

    def test_custom_service_has_base_methods(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that custom services have all base service methods."""
        service = service_class_factory()()

        # Check for key base class methods
        assert hasattr(service, "validate_service")
        assert hasattr(service, "get_service_completeness_report")
        assert hasattr(service, "has_minimum_functionality")
        assert hasattr(service, "process_characteristics")
        assert hasattr(service, "get_missing_characteristics")


# ==============================================================================
# Test: Integration with Characteristics
# ==============================================================================


class TestCharacteristicIntegration:
    """Test integration between services and characteristics."""

    def test_characteristics_dict_is_initialized(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test that characteristics dict is initialized empty."""
        service = service_class_factory()()

        assert hasattr(service, "characteristics")
        assert isinstance(service.characteristics, dict)
        assert len(service.characteristics) == 0

    def test_manual_characteristic_addition(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test manually adding characteristics to service."""
        service = service_class_factory()()

        # Manually add a characteristic
        char = UnknownCharacteristic(
            info=CharacteristicInfo(
                uuid=BluetoothUUID("AAAA0100-0000-1000-8000-00805F9B34FB"),
                name="Test Char",
                unit="",
                value_type=ValueType.BYTES,
                properties=[],
            )
        )

        service.characteristics[char.info.uuid] = char

        assert len(service.characteristics) == 1
        assert char.info.uuid in service.characteristics

    def test_service_validation_with_characteristics(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test service validation works with characteristics."""
        service = service_class_factory()()

        # Add characteristics
        char1 = UnknownCharacteristic(
            info=CharacteristicInfo(
                uuid=BluetoothUUID("AAAA0200-0000-1000-8000-00805F9B34FB"),
                name="Char 1",
                unit="",
                value_type=ValueType.BYTES,
                properties=[],
            )
        )
        char2 = UnknownCharacteristic(
            info=CharacteristicInfo(
                uuid=BluetoothUUID("AAAA0201-0000-1000-8000-00805F9B34FB"),
                name="Char 2",
                unit="",
                value_type=ValueType.BYTES,
                properties=[],
            )
        )

        service.characteristics[char1.info.uuid] = char1
        service.characteristics[char2.info.uuid] = char2

        # Validate service
        result = service.validate_service()
        assert result.is_healthy

        # Check completeness report
        report = service.get_service_completeness_report()
        assert report.characteristics_present == 2


# ==============================================================================
# Test: Edge Cases and Error Handling
# ==============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_process_characteristics_with_missing_properties(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test processing characteristics without properties field."""
        service = service_class_factory()()

        # Characteristic without properties field
        uuid = BluetoothUUID("AAAA0300-0000-1000-8000-00805F9B34FB")
        discovered = {
            uuid: CharacteristicInfo(uuid=uuid, name="", properties=[]),
        }

        service.process_characteristics(discovered)

        assert len(service.characteristics) == 1

    def test_process_characteristics_with_invalid_properties(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test processing characteristics with empty properties."""
        service = service_class_factory()()

        # Empty properties list
        uuid = BluetoothUUID("AAAA0400-0000-1000-8000-00805F9B34FB")
        discovered = {
            uuid: CharacteristicInfo(uuid=uuid, name="", properties=[]),
        }

        service.process_characteristics(discovered)

        # Should still create characteristic (properties just won't be extracted)
        assert len(service.characteristics) == 1

    def test_empty_uuid_string_rejected(self) -> None:
        """Test that empty UUID string is rejected."""
        with pytest.raises((ValueError, TypeError)):
            # This should fail at BluetoothUUID level
            _ = ServiceInfo(
                uuid=BluetoothUUID(""),  # Empty UUID
                name="Bad",
                description="Bad",
            )

    def test_service_with_none_description(
        self, service_class_factory: Callable[..., type[CustomBaseGattService]]
    ) -> None:
        """Test service can have empty description."""
        service = service_class_factory(description="")()
        assert service.summary == ""
