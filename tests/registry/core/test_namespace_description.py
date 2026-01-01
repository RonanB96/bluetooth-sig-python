"""Tests for Namespace Description registry functionality."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from bluetooth_sig.registry.core.namespace_description import (
    NamespaceDescriptionRegistry,
    namespace_description_registry,
)
from bluetooth_sig.types.registry.namespace import NamespaceDescriptionInfo


@pytest.fixture(scope="session")
def registry() -> NamespaceDescriptionRegistry:
    """Create a namespace description registry once per test session."""
    return namespace_description_registry


class TestNamespaceDescriptionRegistry:
    """Test the NamespaceDescriptionRegistry class."""

    def test_registry_initialization(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(registry, NamespaceDescriptionRegistry)
        # Registry should be lazily loaded, not loaded at init
        descriptions = registry.get_all_descriptions()
        assert isinstance(descriptions, dict)
        # Should have descriptions after first access (submodule should be initialized)
        assert len(descriptions) >= 100  # Many namespace descriptions defined
        assert all(isinstance(info, NamespaceDescriptionInfo) for info in descriptions.values())

    def test_lazy_loading(self) -> None:
        """Test that YAML is not loaded until first access."""
        # Create a fresh registry instance
        fresh_registry = NamespaceDescriptionRegistry()
        # _loaded should be False initially (lazy loading)
        assert not fresh_registry._loaded
        # Access should trigger loading
        _ = fresh_registry.is_known_description(0x0001)
        # Now _loaded should be True
        assert fresh_registry._loaded

    def test_get_description_info_ordinal_values(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test lookup by ordinal description values (first, second, etc.)."""
        # Test with ordinal values
        first_info = registry.get_description_info(0x0001)
        assert first_info is not None
        assert isinstance(first_info, NamespaceDescriptionInfo)
        assert first_info.value == 0x0001
        assert first_info.name == "first"

        second_info = registry.get_description_info(0x0002)
        assert second_info is not None
        assert second_info.value == 0x0002
        assert second_info.name == "second"

        tenth_info = registry.get_description_info(0x000A)
        assert tenth_info is not None
        assert tenth_info.value == 0x000A
        assert tenth_info.name == "tenth"

    def test_get_description_info_position_values(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test lookup by position/location description values (left, right, etc.)."""
        # Test with position values (these are in the 0x0100+ range)
        left_info = registry.get_description_info(0x010D)
        assert left_info is not None
        assert isinstance(left_info, NamespaceDescriptionInfo)
        assert left_info.value == 0x010D
        assert left_info.name == "left"

        right_info = registry.get_description_info(0x010E)
        assert right_info is not None
        assert right_info.value == 0x010E
        assert right_info.name == "right"

        top_info = registry.get_description_info(0x0102)
        assert top_info is not None
        assert top_info.value == 0x0102
        assert top_info.name == "top"

        front_info = registry.get_description_info(0x0100)
        assert front_info is not None
        assert front_info.value == 0x0100
        assert front_info.name == "front"

        back_info = registry.get_description_info(0x0101)
        assert back_info is not None
        assert back_info.value == 0x0101
        assert back_info.name == "back"

    def test_get_description_by_name(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test lookup by description name."""
        # Test with known description names
        left_info = registry.get_description_by_name("left")
        assert left_info is not None
        assert isinstance(left_info, NamespaceDescriptionInfo)
        assert left_info.value == 0x010D

        first_info = registry.get_description_by_name("first")
        assert first_info is not None
        assert first_info.value == 0x0001

        # Test case insensitive
        left_upper = registry.get_description_by_name("LEFT")
        assert left_upper == left_info

        # Test not found
        info_none = registry.get_description_by_name("nonexistent")
        assert info_none is None

    def test_is_known_description(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test checking if description value is known."""
        # Known description values should return True
        assert registry.is_known_description(0x0001)  # first
        assert registry.is_known_description(0x010D)  # left
        assert registry.is_known_description(0x010E)  # right
        assert registry.is_known_description(0x0100)  # front

        # Unknown description value
        assert not registry.is_known_description(0xFFFF)  # Not a valid description

    def test_get_description_not_found(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test lookup for non-existent description value."""
        # Non-existent description value
        info = registry.get_description_info(0xFFFF)
        assert info is None

        # Non-existent name
        info = registry.get_description_by_name("nonexistent")
        assert info is None

    def test_get_all_descriptions(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test getting all namespace descriptions."""
        descriptions = registry.get_all_descriptions()
        assert isinstance(descriptions, dict)
        # Should have many descriptions (ordinals 1-255 + positions)
        assert len(descriptions) >= 100
        # Verify ordinal and position values are present
        assert 0x0001 in descriptions
        assert descriptions[0x0001].name == "first"
        assert 0x010D in descriptions
        assert descriptions[0x010D].name == "left"

    def test_resolve_description_name(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test the convenience resolve_description_name method."""
        # Known descriptions should return the name string
        assert registry.resolve_description_name(0x0001) == "first"
        assert registry.resolve_description_name(0x010D) == "left"
        assert registry.resolve_description_name(0x010E) == "right"
        assert registry.resolve_description_name(0x0100) == "front"

        # Unknown description should return None
        assert registry.resolve_description_name(0xFFFF) is None

    def test_thread_safety(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test that registry is thread-safe during concurrent access."""

        def lookup_description(value: int) -> str | None:
            info = registry.get_description_info(value)
            return info.name if info else None

        # Perform concurrent lookups
        values = [0x0001, 0x010D, 0x010E, 0x0100, 0x0002, 0x0003]
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(lookup_description, v) for v in values * 10]
            results = [f.result() for f in futures]

        # Verify all results are correct
        expected = ["first", "left", "right", "front", "second", "third"] * 10
        assert results == expected

    def test_unknown_value_zero(self, registry: NamespaceDescriptionRegistry) -> None:
        """Test lookup of description value 0x0000 (unknown)."""
        unknown_info = registry.get_description_info(0x0000)
        assert unknown_info is not None
        assert unknown_info.value == 0x0000
        assert unknown_info.name == "unknown"
