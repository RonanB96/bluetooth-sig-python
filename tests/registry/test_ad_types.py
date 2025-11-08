"""Tests for AD types registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.ad_types import ADTypesRegistry, ad_types_registry
from bluetooth_sig.types.advertising import ADTypeInfo


@pytest.fixture(scope="session")
def registry() -> ADTypesRegistry:
    """Create an AD types registry once per test session."""
    return ad_types_registry


class TestADTypesRegistry:
    """Test the ADTypesRegistry class."""

    def test_registry_initialization(self, registry: ADTypesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(registry, ADTypesRegistry)
        # Registry should be lazily loaded, not loaded at init
        ad_types = registry.get_all_ad_types()
        assert isinstance(ad_types, dict)
        # If submodule is initialized, should have AD types after first access
        if ad_types:
            assert all(isinstance(info, ADTypeInfo) for info in ad_types.values())

    def test_lazy_loading(self) -> None:
        """Test that YAML is not loaded until first access."""
        # Create a fresh registry instance
        fresh_registry = ADTypesRegistry()
        # _loaded should be False initially (lazy loading)
        assert not fresh_registry._loaded
        # Access should trigger loading
        _ = fresh_registry.is_known_ad_type(0x01)
        # Now _loaded should be True
        assert fresh_registry._loaded

    def test_get_ad_type_info_by_value(self, registry: ADTypesRegistry) -> None:
        """Test lookup by AD type value."""
        # Test with known AD types
        flags_info = registry.get_ad_type_info(0x01)
        if flags_info:  # Only if YAML loaded
            assert isinstance(flags_info, ADTypeInfo)
            assert flags_info.value == 0x01
            assert "flags" in flags_info.name.lower()

        complete_name_info = registry.get_ad_type_info(0x09)
        if complete_name_info:
            assert isinstance(complete_name_info, ADTypeInfo)
            assert complete_name_info.value == 0x09
            assert "complete local name" in complete_name_info.name.lower()

        manufacturer_info = registry.get_ad_type_info(0xFF)
        if manufacturer_info:
            assert isinstance(manufacturer_info, ADTypeInfo)
            assert manufacturer_info.value == 0xFF
            assert "manufacturer" in manufacturer_info.name.lower()

    def test_get_ad_type_by_name(self, registry: ADTypesRegistry) -> None:
        """Test lookup by AD type name."""
        # Test with known AD type name
        flags_info = registry.get_ad_type_by_name("Flags")
        if flags_info:  # Only if YAML loaded
            assert isinstance(flags_info, ADTypeInfo)
            assert flags_info.value == 0x01

        # Test case insensitive
        flags_info_lower = registry.get_ad_type_by_name("flags")
        assert flags_info_lower == flags_info

        # Test not found
        info_none = registry.get_ad_type_by_name("Nonexistent AD Type")
        assert info_none is None

    def test_is_known_ad_type(self, registry: ADTypesRegistry) -> None:
        """Test checking if AD type is known."""
        # Known AD types
        assert registry.is_known_ad_type(0x01) or not registry.get_all_ad_types()  # Flags
        assert registry.is_known_ad_type(0x09) or not registry.get_all_ad_types()  # Complete Local Name
        assert registry.is_known_ad_type(0xFF) or not registry.get_all_ad_types()  # Manufacturer Data

        # Unknown AD type
        assert not registry.is_known_ad_type(0xF0)  # Not a valid AD type

    def test_get_ad_type_not_found(self, registry: ADTypesRegistry) -> None:
        """Test lookup for non-existent AD type."""
        # Non-existent AD type value
        info = registry.get_ad_type_info(0xF0)
        assert info is None

        # Non-existent name
        info = registry.get_ad_type_by_name("Nonexistent Type")
        assert info is None

    def test_get_all_ad_types(self, registry: ADTypesRegistry) -> None:
        """Test getting all AD types."""
        ad_types = registry.get_all_ad_types()
        assert isinstance(ad_types, dict)

        # If YAML loaded, should have multiple AD types
        if ad_types:
            assert len(ad_types) > 0
            # Check for some standard AD types
            assert 0x01 in ad_types  # Flags
            assert 0x09 in ad_types  # Complete Local Name
            assert 0xFF in ad_types  # Manufacturer Specific Data

            # Verify all values are ADTypeInfo
            for value, info in ad_types.items():
                assert isinstance(info, ADTypeInfo)
                assert info.value == value

    def test_ad_type_info_structure(self, registry: ADTypesRegistry) -> None:
        """Test that ADTypeInfo has expected structure."""
        info = registry.get_ad_type_info(0x01)
        if info:
            assert hasattr(info, "value")
            assert hasattr(info, "name")
            assert hasattr(info, "reference")
            assert isinstance(info.value, int)
            assert isinstance(info.name, str)
            assert info.reference is None or isinstance(info.reference, str)

    def test_thread_safety(self, registry: ADTypesRegistry) -> None:
        """Test that concurrent lookups work correctly."""
        results: list[ADTypeInfo | None] = []

        def lookup_ad_type(ad_type: int) -> None:
            info = registry.get_ad_type_info(ad_type)
            results.append(info)

        # Test concurrent access
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(10):
                futures.append(executor.submit(lookup_ad_type, 0x01))
            for future in futures:
                future.result()

        # All lookups should have succeeded (or all returned None if YAML not loaded)
        assert len(results) == 10
        # All results should be the same
        assert all(r == results[0] for r in results)

    def test_singleton_instance(self) -> None:
        """Test that ad_types_registry is a singleton."""
        from bluetooth_sig.registry import ad_types_registry as imported_registry

        # Should be the same instance
        assert ad_types_registry is imported_registry

    def test_standard_ad_types_present(self, registry: ADTypesRegistry) -> None:
        """Test that standard AD types are present if YAML is loaded."""
        ad_types = registry.get_all_ad_types()
        if not ad_types:
            pytest.skip("YAML not loaded, skipping standard AD types test")

        # Check for presence of key standard AD types
        standard_types = {
            0x01: "Flags",
            0x02: "16-bit",  # Incomplete List of 16-bit Service UUIDs
            0x03: "16-bit",  # Complete List of 16-bit Service UUIDs
            0x08: "Shortened Local Name",
            0x09: "Complete Local Name",
            0x0A: "Tx Power",
            0x16: "Service Data",
            0xFF: "Manufacturer",
        }

        for value, name_fragment in standard_types.items():
            assert value in ad_types, f"AD type 0x{value:02X} should be present"
            assert name_fragment.lower() in ad_types[value].name.lower()

    def test_reference_field(self, registry: ADTypesRegistry) -> None:
        """Test that reference field is populated when available."""
        info = registry.get_ad_type_info(0x01)
        if info:
            # Flags should have a reference
            assert info.reference is not None
            assert len(info.reference) > 0

    def test_handles_missing_yaml(self) -> None:
        """Test that registry handles missing YAML gracefully."""
        # This is implicitly tested by all other tests that check
        # "if info:" or "if ad_types:" conditions
        fresh_registry = ADTypesRegistry()
        # Should not raise even if YAML is missing
        info = fresh_registry.get_ad_type_info(0x01)
        # Should return None if YAML not found, or valid info if found
        assert info is None or isinstance(info, ADTypeInfo)
