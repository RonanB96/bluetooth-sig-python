"""Tests for declarations registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.uuids.declarations import DeclarationInfo, DeclarationsRegistry
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def declarations_registry() -> DeclarationsRegistry:
    """Create a declarations registry once per test session."""
    return DeclarationsRegistry()


class TestDeclarationsRegistry:
    """Test the DeclarationsRegistry class."""

    def test_registry_initialization(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(declarations_registry, DeclarationsRegistry)
        # Should have loaded some declarations if YAML exists
        declarations = declarations_registry.get_all_declarations()
        assert isinstance(declarations, list)
        # If submodule is initialized, should have declarations
        if declarations:
            assert all(isinstance(decl, DeclarationInfo) for decl in declarations)

    def test_get_declaration_info(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known declaration UUID (Primary Service)
        info = declarations_registry.get_declaration_info("0x2800")
        if info:  # Only if YAML loaded
            assert isinstance(info, DeclarationInfo)
            assert info.name == "Primary Service"
            assert info.id == "org.bluetooth.attribute.gatt.primary_service_declaration"

    def test_get_declaration_info_by_name(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test lookup by declaration name."""
        # Test with known declaration name (Primary Service)
        info = declarations_registry.get_declaration_info_by_name("Primary Service")
        if info:  # Only if YAML loaded
            assert isinstance(info, DeclarationInfo)
            assert info.name == "Primary Service"
            assert info.uuid.short_form.upper() == "2800"

        # Test case insensitive
        info_lower = declarations_registry.get_declaration_info_by_name("primary service")
        assert info_lower == info

        # Test not found
        info_none = declarations_registry.get_declaration_info_by_name("Nonexistent Declaration")
        assert info_none is None

    def test_get_declaration_info_by_id(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test lookup by declaration ID."""
        # Test with known declaration ID
        info = declarations_registry.get_declaration_info_by_id(
            "org.bluetooth.attribute.gatt.primary_service_declaration"
        )
        if info:  # Only if YAML loaded
            assert isinstance(info, DeclarationInfo)
            assert info.name == "Primary Service"
            assert info.uuid.short_form.upper() == "2800"

        # Test not found
        info_none = declarations_registry.get_declaration_info_by_id("org.bluetooth.attribute.gatt.nonexistent")
        assert info_none is None

    def test_get_declaration_info_by_bluetooth_uuid(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known declaration
        bt_uuid = BluetoothUUID("2800")
        info = declarations_registry.get_declaration_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, DeclarationInfo)
            assert info.name == "Primary Service"

    def test_get_declaration_info_not_found(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test lookup for non-existent declaration."""
        info = declarations_registry.get_declaration_info("nonexistent")
        assert info is None

        info = declarations_registry.get_declaration_info("0x0000")  # Not a declaration UUID
        assert info is None

    def test_is_declaration_uuid(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test declaration UUID validation."""
        # Known declaration UUID
        has_declarations = bool(declarations_registry.get_all_declarations())
        assert declarations_registry.is_declaration_uuid("0x2800") or not has_declarations

        # Non-declaration UUID
        assert not declarations_registry.is_declaration_uuid("0x0000")

        # Invalid UUID
        assert not declarations_registry.is_declaration_uuid("invalid")

    def test_get_all_declarations(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test getting all declarations."""
        declarations = declarations_registry.get_all_declarations()
        assert isinstance(declarations, list)

        if declarations:
            # If loaded, check structure
            for declaration in declarations:
                assert isinstance(declaration, DeclarationInfo)
                assert isinstance(declaration.name, str)
                assert isinstance(declaration.uuid, BluetoothUUID)
                assert isinstance(declaration.id, str)
                # Should be 16-bit UUIDs
                assert len(declaration.uuid.short_form) == 4

    def test_declaration_info_structure(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test DeclarationInfo dataclass structure."""
        declarations = declarations_registry.get_all_declarations()
        if declarations:
            declaration = declarations[0]
            assert hasattr(declaration, "uuid")
            assert hasattr(declaration, "name")
            assert hasattr(declaration, "id")
            assert isinstance(declaration.uuid, BluetoothUUID)
            assert isinstance(declaration.name, str)
            assert isinstance(declaration.id, str)

    def test_uuid_formats(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | int] = ["2800", "0x2800", "0X2800", 0x2800]
        for fmt in formats:
            info = declarations_registry.get_declaration_info(fmt)
            if declarations_registry.is_declaration_uuid("2800"):
                assert info is not None
                assert info.name == "Primary Service"

    def test_known_declarations(self, declarations_registry: DeclarationsRegistry) -> None:
        """Test lookup for known GATT declarations."""
        # Test Primary Service
        primary_service = declarations_registry.get_declaration_info("0x2800")
        if primary_service:
            assert primary_service.name == "Primary Service"
            assert primary_service.id == "org.bluetooth.attribute.gatt.primary_service_declaration"

        # Test Secondary Service
        secondary_service = declarations_registry.get_declaration_info("0x2801")
        if secondary_service:
            assert secondary_service.name == "Secondary Service"
            assert secondary_service.id == "org.bluetooth.attribute.gatt.secondary_service_declaration"

        # Test Include
        include = declarations_registry.get_declaration_info("0x2802")
        if include:
            assert include.name == "Include"
            assert include.id == "org.bluetooth.attribute.gatt.include_declaration"

        # Test Characteristic
        characteristic = declarations_registry.get_declaration_info("0x2803")
        if characteristic:
            assert characteristic.name == "Characteristic"
            assert characteristic.id == "org.bluetooth.attribute.gatt.characteristic_declaration"
