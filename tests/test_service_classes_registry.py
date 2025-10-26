"""Tests for service classes registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.service_classes import ServiceClassesRegistry, ServiceClassInfo
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def service_classes_registry() -> ServiceClassesRegistry:
    """Create a service classes registry once per test session."""
    return ServiceClassesRegistry()


class TestServiceClassesRegistry:
    """Test the ServiceClassesRegistry class."""

    def test_registry_initialization(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(service_classes_registry, ServiceClassesRegistry)
        # Should have loaded some service classes if YAML exists
        service_classes = service_classes_registry.get_all_service_classes()
        assert isinstance(service_classes, list)
        # If submodule is initialized, should have service classes
        if service_classes:
            assert all(isinstance(sc, ServiceClassInfo) for sc in service_classes)

    def test_get_service_class_info(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known service class UUID (Generic Access)
        info = service_classes_registry.get_service_class_info("0x1800")
        if info:  # Only if YAML loaded
            assert isinstance(info, ServiceClassInfo)
            assert info.name == "Generic Access"
            assert info.id == "org.bluetooth.service.generic_access"

    def test_get_service_class_info_by_name(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test lookup by service class name."""
        # Test with known service class name (Generic Access)
        info = service_classes_registry.get_service_class_info_by_name("Generic Access")
        if info:  # Only if YAML loaded
            assert isinstance(info, ServiceClassInfo)
            assert info.name == "Generic Access"
            assert info.uuid.short_form.upper() == "1800"

        # Test case insensitive
        info_lower = service_classes_registry.get_service_class_info_by_name("generic access")
        assert info_lower == info

        # Test not found
        info_none = service_classes_registry.get_service_class_info_by_name("Nonexistent Service Class")
        assert info_none is None

    def test_get_service_class_info_by_id(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test lookup by service class ID."""
        # Test with known service class ID
        info = service_classes_registry.get_service_class_info_by_id("org.bluetooth.service.generic_access")
        if info:  # Only if YAML loaded
            assert isinstance(info, ServiceClassInfo)
            assert info.name == "Generic Access"
            assert info.uuid.short_form.upper() == "1800"

        # Test not found
        info_none = service_classes_registry.get_service_class_info_by_id("org.bluetooth.service.nonexistent")
        assert info_none is None

    def test_get_service_class_info_by_bluetooth_uuid(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known service class
        bt_uuid = BluetoothUUID("1800")
        info = service_classes_registry.get_service_class_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, ServiceClassInfo)
            assert info.name == "Generic Access"

    def test_get_service_class_info_not_found(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test lookup for non-existent service class."""
        info = service_classes_registry.get_service_class_info("nonexistent")
        assert info is None

        info = service_classes_registry.get_service_class_info("0x0000")  # Not a service class UUID
        assert info is None

    def test_is_service_class_uuid(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test service class UUID validation."""
        # Known service class UUID
        has_service_classes = bool(service_classes_registry.get_all_service_classes())
        assert service_classes_registry.is_service_class_uuid("0x1800") or not has_service_classes

        # Non-service class UUID
        assert not service_classes_registry.is_service_class_uuid("0x0000")

        # Invalid UUID
        assert not service_classes_registry.is_service_class_uuid("invalid")

    def test_get_all_service_classes(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test getting all service classes."""
        service_classes = service_classes_registry.get_all_service_classes()
        assert isinstance(service_classes, list)

        if service_classes:
            # If loaded, check structure
            for service_class in service_classes:
                assert isinstance(service_class, ServiceClassInfo)
                assert isinstance(service_class.name, str)
                assert isinstance(service_class.uuid, BluetoothUUID)
                assert isinstance(service_class.id, str)
                # Should be 16-bit UUIDs
                assert len(service_class.uuid.short_form) == 4

    def test_service_class_info_structure(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test ServiceClassInfo dataclass structure."""
        service_classes = service_classes_registry.get_all_service_classes()
        if service_classes:
            service_class = service_classes[0]
            assert hasattr(service_class, "uuid")
            assert hasattr(service_class, "name")
            assert hasattr(service_class, "id")
            assert isinstance(service_class.uuid, BluetoothUUID)
            assert isinstance(service_class.name, str)
            assert isinstance(service_class.id, str)

    def test_uuid_formats(self, service_classes_registry: ServiceClassesRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | int] = ["1800", "0x1800", "0X1800", 0x1800]
        for fmt in formats:
            info = service_classes_registry.get_service_class_info(fmt)
            if service_classes_registry.is_service_class_uuid("1800"):
                assert info is not None
                assert info.name == "Generic Access"
