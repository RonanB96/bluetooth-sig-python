"""Tests for Permitted Characteristics Registry."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.profiles.permitted_characteristics import (
    PermittedCharacteristicsRegistry,
)
from bluetooth_sig.types.registry.profile_types import PermittedCharacteristicEntry


@pytest.fixture(scope="session")
def perm_registry() -> PermittedCharacteristicsRegistry:
    """Create a permitted characteristics registry once per test session."""
    return PermittedCharacteristicsRegistry()


class TestPermittedCharacteristicsRegistryInit:
    """Initialisation and lazy-loading tests."""

    def test_registry_initialization(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """Registry creates without error."""
        assert isinstance(perm_registry, PermittedCharacteristicsRegistry)

    def test_lazy_loading(self) -> None:
        """Data is not loaded until first query."""
        reg = PermittedCharacteristicsRegistry()
        assert not reg._loaded

        _ = reg.get_all_profiles()
        assert reg._loaded


class TestPermittedCharacteristicsLoading:
    """Tests that validate YAML data is loaded correctly."""

    def test_all_profiles_loaded(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """ESS, UDS and IMDS profiles should all be present."""
        profiles = perm_registry.get_all_profiles()
        assert "ess" in profiles
        assert "uds" in profiles
        assert "imds" in profiles

    def test_ess_characteristics_count(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """ESS should have ~31 permitted characteristics."""
        chars = perm_registry.get_permitted_characteristics("ess")
        assert len(chars) >= 25

    def test_uds_characteristics_count(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """UDS should have ~39 permitted characteristics."""
        chars = perm_registry.get_permitted_characteristics("uds")
        assert len(chars) >= 30

    def test_imds_characteristics_count(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """IMDS should have ~7 permitted characteristics."""
        chars = perm_registry.get_permitted_characteristics("imds")
        assert len(chars) >= 5

    def test_characteristics_are_uri_strings(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """All characteristic identifiers should be org.bluetooth.characteristic.* URIs."""
        for profile in perm_registry.get_all_profiles():
            for char_id in perm_registry.get_permitted_characteristics(profile):
                assert char_id.startswith("org.bluetooth.characteristic."), (
                    f"{profile}: unexpected URI format: {char_id}"
                )

    def test_unknown_profile_returns_empty(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """Querying a non-existent profile returns an empty list."""
        assert perm_registry.get_permitted_characteristics("nonexistent") == []


class TestPermittedCharacteristicsEntries:
    """Tests for the structured get_entries API."""

    def test_get_entries_returns_structs(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """get_entries returns PermittedCharacteristicEntry structs."""
        entries = perm_registry.get_entries("ess")
        assert len(entries) >= 1
        assert all(isinstance(e, PermittedCharacteristicEntry) for e in entries)

    def test_entry_service_field(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """Each entry has a service field starting with org.bluetooth.service."""
        for profile in perm_registry.get_all_profiles():
            for entry in perm_registry.get_entries(profile):
                assert entry.service.startswith("org.bluetooth.service."), (
                    f"{profile}: unexpected service URI: {entry.service}"
                )

    def test_entry_characteristics_is_tuple(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """Characteristics field should be a tuple (immutable)."""
        entries = perm_registry.get_entries("ess")
        assert entries  # non-empty
        assert isinstance(entries[0].characteristics, tuple)

    def test_entries_unknown_profile(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """get_entries for unknown profile returns empty list."""
        assert perm_registry.get_entries("nonexistent") == []


class TestReturnedListsAreDefensiveCopies:
    """Mutations on returned lists must not affect registry state."""

    def test_characteristics_copy(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """Mutating the returned characteristics list is safe."""
        chars1 = perm_registry.get_permitted_characteristics("ess")
        original_len = len(chars1)
        chars1.clear()

        chars2 = perm_registry.get_permitted_characteristics("ess")
        assert len(chars2) == original_len

    def test_entries_copy(self, perm_registry: PermittedCharacteristicsRegistry) -> None:
        """Mutating the returned entries list is safe."""
        entries1 = perm_registry.get_entries("ess")
        original_len = len(entries1)
        entries1.clear()

        entries2 = perm_registry.get_entries("ess")
        assert len(entries2) == original_len
