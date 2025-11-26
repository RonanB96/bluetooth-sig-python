"""Tests for units registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.common import UuidInfo
from bluetooth_sig.registry.uuids.units import UnitsRegistry
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def units_registry() -> UnitsRegistry:
    """Create a units registry once per test session."""
    return UnitsRegistry()


class TestUnitsRegistry:
    """Test the UnitsRegistry class."""

    def test_registry_initialization(self, units_registry: UnitsRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(units_registry, UnitsRegistry)
        # Should have loaded some units if YAML exists
        units = units_registry.get_all_units()
        assert isinstance(units, list)
        # If submodule is initialized, should have units
        if units:
            assert all(isinstance(u, UuidInfo) for u in units)

    def test_get_unit_info(self, units_registry: UnitsRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known unit UUID (unitless)
        info = units_registry.get_unit_info("0x2700")
        if info:  # Only if YAML loaded
            assert isinstance(info, UuidInfo)
            assert info.name == "unitless"
            assert info.id == "org.bluetooth.unit.unitless"

    def test_get_unit_info_by_name(self, units_registry: UnitsRegistry) -> None:
        """Test lookup by unit name."""
        # Test with known unit name (unitless)
        info = units_registry.get_unit_info_by_name("unitless")
        if info:  # Only if YAML loaded
            assert isinstance(info, UuidInfo)
            assert info.name == "unitless"
            assert info.uuid.short_form.upper() == "2700"

        # Test case insensitive
        info_lower = units_registry.get_unit_info_by_name("Unitless")
        assert info_lower == info

        # Test not found
        info_none = units_registry.get_unit_info_by_name("Nonexistent Unit")
        assert info_none is None

    def test_get_unit_info_by_id(self, units_registry: UnitsRegistry) -> None:
        """Test lookup by unit ID."""
        # Test with known unit ID
        info = units_registry.get_unit_info_by_id("org.bluetooth.unit.unitless")
        if info:  # Only if YAML loaded
            assert isinstance(info, UuidInfo)
            assert info.name == "unitless"
            assert info.uuid.short_form.upper() == "2700"

        # Test not found
        info_none = units_registry.get_unit_info_by_id("org.bluetooth.unit.nonexistent")
        assert info_none is None

    def test_get_unit_info_by_bluetooth_uuid(self, units_registry: UnitsRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known unit
        bt_uuid = BluetoothUUID("2700")
        info = units_registry.get_unit_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, UuidInfo)
            assert info.name == "unitless"

    def test_get_unit_info_not_found(self, units_registry: UnitsRegistry) -> None:
        """Test lookup for non-existent unit."""
        info = units_registry.get_unit_info("nonexistent")
        assert info is None

        info = units_registry.get_unit_info("0x0000")  # Not a unit UUID
        assert info is None

    def test_is_unit_uuid(self, units_registry: UnitsRegistry) -> None:
        """Test unit UUID validation."""
        # Known unit UUID
        assert units_registry.is_unit_uuid("0x2700") or not units_registry.get_all_units()

        # Non-unit UUID
        assert not units_registry.is_unit_uuid("0x0000")

        # Invalid UUID
        assert not units_registry.is_unit_uuid("invalid")

    def test_get_all_units(self, units_registry: UnitsRegistry) -> None:
        """Test getting all units."""
        units = units_registry.get_all_units()
        assert isinstance(units, list)

        if units:
            # If loaded, check structure
            for unit in units:
                assert isinstance(unit, UuidInfo)
                assert isinstance(unit.name, str)
                assert isinstance(unit.uuid, BluetoothUUID)
                assert isinstance(unit.id, str)
                # Should be 16-bit UUIDs
                assert len(unit.uuid.short_form) == 4

    def test_unit_info_structure(self, units_registry: UnitsRegistry) -> None:
        """Test UuidInfo dataclass structure."""
        units = units_registry.get_all_units()
        if units:
            unit = units[0]
            assert hasattr(unit, "uuid")
            assert hasattr(unit, "name")
            assert hasattr(unit, "id")
            assert isinstance(unit.uuid, BluetoothUUID)
            assert isinstance(unit.name, str)
            assert isinstance(unit.id, str)

    def test_uuid_formats(self, units_registry: UnitsRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str] = ["2700", "0x2700", "0X2700"]
        for fmt in formats:
            info = units_registry.get_unit_info(fmt)
            assert info is not None
            assert info.name == "unitless"
