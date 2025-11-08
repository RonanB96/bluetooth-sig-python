"""Tests for object types registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.uuids.object_types import ObjectTypeInfo, ObjectTypesRegistry
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def object_types_registry() -> ObjectTypesRegistry:
    """Create an object types registry once per test session."""
    return ObjectTypesRegistry()


class TestObjectTypesRegistry:
    """Test the ObjectTypesRegistry class."""

    def test_registry_initialization(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(object_types_registry, ObjectTypesRegistry)
        # Should have loaded some object types if YAML exists
        object_types = object_types_registry.get_all_object_types()
        assert isinstance(object_types, list)
        # If submodule is initialized, should have object types
        if object_types:
            assert all(isinstance(ot, ObjectTypeInfo) for ot in object_types)

    def test_get_object_type_info(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known object type UUID (Unspecified)
        info = object_types_registry.get_object_type_info("0x2ACA")
        if info:  # Only if YAML loaded
            assert isinstance(info, ObjectTypeInfo)
            assert info.name == "Unspecified"
            assert info.id == "org.bluetooth.object.unspecified"

    def test_get_object_type_info_by_name(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test lookup by object type name."""
        # Test with known object type name (Unspecified)
        info = object_types_registry.get_object_type_info_by_name("Unspecified")
        if info:  # Only if YAML loaded
            assert isinstance(info, ObjectTypeInfo)
            assert info.name == "Unspecified"
            assert info.uuid.short_form.upper() == "2ACA"

        # Test case insensitive
        info_lower = object_types_registry.get_object_type_info_by_name("unspecified")
        assert info_lower == info

        # Test not found
        info_none = object_types_registry.get_object_type_info_by_name("Nonexistent Object Type")
        assert info_none is None

    def test_get_object_type_info_by_id(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test lookup by object type ID."""
        # Test with known object type ID
        info = object_types_registry.get_object_type_info_by_id("org.bluetooth.object.unspecified")
        if info:  # Only if YAML loaded
            assert isinstance(info, ObjectTypeInfo)
            assert info.name == "Unspecified"
            assert info.uuid.short_form.upper() == "2ACA"

        # Test not found
        info_none = object_types_registry.get_object_type_info_by_id("org.bluetooth.object.nonexistent")
        assert info_none is None

    def test_get_object_type_info_by_bluetooth_uuid(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known object type
        bt_uuid = BluetoothUUID("2ACA")
        info = object_types_registry.get_object_type_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, ObjectTypeInfo)
            assert info.name == "Unspecified"

    def test_get_object_type_info_not_found(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test lookup for non-existent object type."""
        info = object_types_registry.get_object_type_info("nonexistent")
        assert info is None

        info = object_types_registry.get_object_type_info("0x0000")  # Not an object type UUID
        assert info is None

    def test_is_object_type_uuid(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test object type UUID validation."""
        # Known object type UUID
        assert object_types_registry.is_object_type_uuid("0x2ACA") or not object_types_registry.get_all_object_types()

        # Non-object type UUID
        assert not object_types_registry.is_object_type_uuid("0x0000")

        # Invalid UUID
        assert not object_types_registry.is_object_type_uuid("invalid")

    def test_get_all_object_types(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test getting all object types."""
        object_types = object_types_registry.get_all_object_types()
        assert isinstance(object_types, list)

        if object_types:
            # If loaded, check structure
            for object_type in object_types:
                assert isinstance(object_type, ObjectTypeInfo)
                assert isinstance(object_type.name, str)
                assert isinstance(object_type.uuid, BluetoothUUID)
                assert isinstance(object_type.id, str)
                # Should be 16-bit UUIDs
                assert len(object_type.uuid.short_form) == 4

    def test_object_type_info_structure(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test ObjectTypeInfo dataclass structure."""
        object_types = object_types_registry.get_all_object_types()
        if object_types:
            object_type = object_types[0]
            assert hasattr(object_type, "uuid")
            assert hasattr(object_type, "name")
            assert hasattr(object_type, "id")
            assert isinstance(object_type.uuid, BluetoothUUID)
            assert isinstance(object_type.name, str)
            assert isinstance(object_type.id, str)

    def test_uuid_formats(self, object_types_registry: ObjectTypesRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | int] = ["2ACA", "0x2ACA", "0X2ACA", 0x2ACA]
        for fmt in formats:
            info = object_types_registry.get_object_type_info(fmt)
            if object_types_registry.is_object_type_uuid("2ACA"):
                assert info is not None
                assert info.name == "Unspecified"
