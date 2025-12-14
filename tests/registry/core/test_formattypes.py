"""Tests for format types registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.formattypes import FormatTypesRegistry, format_types_registry
from bluetooth_sig.types.registry.formattypes import FormatTypeInfo


@pytest.fixture(scope="session")
def registry() -> FormatTypesRegistry:
    """Create a format types registry once per test session."""
    return format_types_registry


class TestFormatTypesRegistry:
    """Test the FormatTypesRegistry class."""

    def test_registry_initialization(self, registry: FormatTypesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(registry, FormatTypesRegistry)
        # Registry should be lazily loaded, not loaded at init
        format_types = registry.get_all_format_types()
        assert isinstance(format_types, dict)
        # Should have format types after first access (submodule should be initialized)
        assert len(format_types) >= 28  # Official Bluetooth format types
        assert all(isinstance(info, FormatTypeInfo) for info in format_types.values())

    def test_lazy_loading(self) -> None:
        """Test that YAML is not loaded until first access."""
        # Create a fresh registry instance
        fresh_registry = FormatTypesRegistry()
        # _loaded should be False initially (lazy loading)
        assert not fresh_registry._loaded
        # Access should trigger loading
        _ = fresh_registry.is_known_format_type(0x01)
        # Now _loaded should be True
        assert fresh_registry._loaded

    def test_get_format_type_info_by_value(self, registry: FormatTypesRegistry) -> None:
        """Test lookup by format type value."""
        # Test with known format types - registry should be loaded
        boolean_info = registry.get_format_type_info(0x01)
        assert boolean_info is not None
        assert isinstance(boolean_info, FormatTypeInfo)
        assert boolean_info.value == 0x01
        assert "boolean" in boolean_info.short_name.lower()

        utf8s_info = registry.get_format_type_info(0x19)
        assert utf8s_info is not None
        assert isinstance(utf8s_info, FormatTypeInfo)
        assert utf8s_info.value == 0x19
        assert utf8s_info.short_name == "utf8s"

        utf16s_info = registry.get_format_type_info(0x1A)
        assert utf16s_info is not None
        assert isinstance(utf16s_info, FormatTypeInfo)
        assert utf16s_info.value == 0x1A
        assert utf16s_info.short_name == "utf16s"

        struct_info = registry.get_format_type_info(0x1B)
        assert struct_info is not None
        assert isinstance(struct_info, FormatTypeInfo)
        assert struct_info.value == 0x1B
        assert struct_info.short_name == "struct"

    def test_get_format_type_by_name(self, registry: FormatTypesRegistry) -> None:
        """Test lookup by format type name."""
        # Test with known format type names - registry should be loaded
        boolean_info = registry.get_format_type_by_name("boolean")
        assert boolean_info is not None
        assert isinstance(boolean_info, FormatTypeInfo)
        assert boolean_info.value == 0x01

        utf8s_info = registry.get_format_type_by_name("utf8s")
        assert utf8s_info is not None
        assert isinstance(utf8s_info, FormatTypeInfo)
        assert utf8s_info.value == 0x19

        utf16s_info = registry.get_format_type_by_name("utf16s")
        assert utf16s_info is not None
        assert isinstance(utf16s_info, FormatTypeInfo)
        assert utf16s_info.value == 0x1A

        # Test case insensitive
        boolean_lower = registry.get_format_type_by_name("BOOLEAN")
        assert boolean_lower == boolean_info

        # Test not found
        info_none = registry.get_format_type_by_name("nonexistent")
        assert info_none is None

    def test_is_known_format_type(self, registry: FormatTypesRegistry) -> None:
        """Test checking if format type is known."""
        # When YAML is loaded, known format types should return True
        assert registry.is_known_format_type(0x01)  # boolean
        assert registry.is_known_format_type(0x19)  # utf8s
        assert registry.is_known_format_type(0x1A)  # utf16s
        assert registry.is_known_format_type(0x1B)  # struct
        # Unknown format type should always return False
        assert not registry.is_known_format_type(0x00)  # Not a valid format type

    def test_get_format_type_not_found(self, registry: FormatTypesRegistry) -> None:
        """Test lookup for non-existent format type."""
        # Non-existent format type value
        info = registry.get_format_type_info(0x00)
        assert info is None

        # Non-existent name
        info = registry.get_format_type_by_name("nonexistent")
        assert info is None

    def test_get_all_format_types(self, registry: FormatTypesRegistry) -> None:
        """Test getting all format types."""
        format_types = registry.get_all_format_types()
        assert isinstance(format_types, dict)
        assert len(format_types) >= 28  # Official Bluetooth format types

        # Check for some standard format types
        assert 0x01 in format_types  # boolean
        assert 0x19 in format_types  # utf8s
        assert 0x1A in format_types  # utf16s
        assert 0x1B in format_types  # struct

        # Verify all values are FormatTypeInfo
        for value, info in format_types.items():
            assert isinstance(info, FormatTypeInfo)
            assert info.value == value

    def test_format_type_info_structure(self, registry: FormatTypesRegistry) -> None:
        """Test that FormatTypeInfo has expected structure."""
        info = registry.get_format_type_info(0x01)
        assert info is not None
        assert hasattr(info, "value")
        assert hasattr(info, "short_name")
        assert hasattr(info, "description")
        assert hasattr(info, "exponent")
        assert hasattr(info, "size")
        assert isinstance(info.value, int)
        assert isinstance(info.short_name, str)
        assert isinstance(info.description, str)
        assert isinstance(info.exponent, bool)
        assert isinstance(info.size, int)

    def test_thread_safety(self, registry: FormatTypesRegistry) -> None:
        """Test that concurrent lookups work correctly."""
        results: list[FormatTypeInfo | None] = []

        def lookup_format_type(value: int) -> None:
            info = registry.get_format_type_info(value)
            results.append(info)

        # Test concurrent access
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(10):
                futures.append(executor.submit(lookup_format_type, 0x01))
            for future in futures:
                future.result()

        # All lookups should have succeeded and returned the same result
        assert len(results) == 10
        assert all(r is not None for r in results)  # All should be FormatTypeInfo objects
        assert all(r == results[0] for r in results)  # All results should be identical

    def test_singleton_instance(self) -> None:
        """Test that format_types_registry is a singleton."""
        from bluetooth_sig.registry.core.formattypes import format_types_registry as imported_registry

        # Should be the same instance
        assert format_types_registry is imported_registry

    def test_standard_format_types_present(self, registry: FormatTypesRegistry) -> None:
        """Test that standard format types are present."""
        format_types = registry.get_all_format_types()

        # Check for presence of key standard format types
        standard_types = {
            0x01: "boolean",
            0x02: "uint2",
            0x03: "uint4",
            0x04: "uint8",
            0x19: "utf8s",
            0x1A: "utf16s",
            0x1B: "struct",
        }

        for value, short_name in standard_types.items():
            assert value in format_types, f"Format type 0x{value:02X} should be present"
            assert format_types[value].short_name == short_name

    def test_handles_missing_yaml(self) -> None:
        """Test that registry handles missing YAML gracefully."""
        fresh_registry = FormatTypesRegistry()
        # Should not raise even if YAML is missing
        info = fresh_registry.get_format_type_info(0x01)
        # In a properly set up environment, should return valid info
        # (this test assumes the submodule is initialized)
        assert info is not None
        assert isinstance(info, FormatTypeInfo)
