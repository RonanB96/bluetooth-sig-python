"""Tests for Profile Lookup Registry."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.profiles.profile_lookup import ProfileLookupRegistry
from bluetooth_sig.types.registry.profile_types import ProfileLookupEntry


@pytest.fixture(scope="session")
def lookup_registry() -> ProfileLookupRegistry:
    """Create a profile lookup registry once per test session."""
    return ProfileLookupRegistry()


class TestProfileLookupRegistryInit:
    """Initialisation and lazy-loading tests."""

    def test_registry_initialization(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Registry creates without error."""
        assert isinstance(lookup_registry, ProfileLookupRegistry)

    def test_lazy_loading(self) -> None:
        """Data is not loaded until first query."""
        reg = ProfileLookupRegistry()
        assert not reg._loaded

        _ = reg.get_all_table_keys()
        assert reg._loaded


class TestProfileLookupLoading:
    """Tests that validate YAML data is loaded correctly."""

    def test_tables_loaded(self, lookup_registry: ProfileLookupRegistry) -> None:
        """At least the expected number of lookup tables are loaded."""
        keys = lookup_registry.get_all_table_keys()
        assert len(keys) >= 15
        # Well-known tables
        assert "audio_codec_id" in keys
        assert "bearer_technology" in keys
        assert "display_types" in keys

    def test_bearer_technology_entries(self, lookup_registry: ProfileLookupRegistry) -> None:
        """bearer_technology should have known entries like 3G, 4G, LTE."""
        entries = lookup_registry.get_entries("bearer_technology")
        assert len(entries) >= 5
        assert all(isinstance(e, ProfileLookupEntry) for e in entries)

        names = {e.name for e in entries}
        assert "3G" in names
        assert "LTE" in names

    def test_audio_codec_id_has_sbc(self, lookup_registry: ProfileLookupRegistry) -> None:
        """audio_codec_id should include SBC as the mandatory A2DP codec."""
        entries = lookup_registry.get_entries("audio_codec_id")
        assert any(e.name == "SBC" for e in entries)

    def test_audio_codec_id_metadata(self, lookup_registry: ProfileLookupRegistry) -> None:
        """audio_codec_id entries should carry metadata (specified_in, used_in)."""
        entries = lookup_registry.get_entries("audio_codec_id")
        sbc = next(e for e in entries if e.name == "SBC")
        assert "specified_in" in sbc.metadata
        assert sbc.metadata["specified_in"] == "A2DP"

    def test_entry_values_are_ints(self, lookup_registry: ProfileLookupRegistry) -> None:
        """All entry values should be integers."""
        for key in lookup_registry.get_all_table_keys():
            for entry in lookup_registry.get_entries(key):
                assert isinstance(entry.value, int), f"{key}/{entry.name}: value is not int"

    def test_unknown_table_returns_empty(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Querying a non-existent table returns an empty list."""
        assert lookup_registry.get_entries("nonexistent_table") == []

    def test_ltv_files_not_loaded(self, lookup_registry: ProfileLookupRegistry) -> None:
        """LTV / codec capability structures should be deferred (not loaded)."""
        keys = lookup_registry.get_all_table_keys()
        # These are LTV-specific keys that should NOT appear
        ltv_keys = {
            "supported_sampling_frequencies",
            "supported_frame_durations",
            "supported_audio_channel_counts",
            "supported_octets_per_codec_frame",
            "sampling_frequency_configuration",
        }
        loaded_ltv = ltv_keys & set(keys)
        assert not loaded_ltv, f"LTV tables should be deferred: {loaded_ltv}"

    def test_permitted_characteristics_not_loaded(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Permitted characteristics files should not appear in lookup tables."""
        keys = lookup_registry.get_all_table_keys()
        assert "permitted_characteristics" not in keys


class TestProfileLookupResolve:
    """Tests for the resolve_name convenience method."""

    def test_resolve_known_name(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Resolving a known value returns the expected name."""
        # 3G in bearer_technology has value 1
        name = lookup_registry.resolve_name("bearer_technology", 1)
        assert name == "3G"

    def test_resolve_unknown_value(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Resolving an unknown value returns None."""
        assert lookup_registry.resolve_name("bearer_technology", 0xFFFF) is None

    def test_resolve_unknown_table(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Resolving in an unknown table returns None."""
        assert lookup_registry.resolve_name("nonexistent", 0) is None


class TestReturnedListsAreDefensiveCopies:
    """Mutations on returned lists must not affect registry state."""

    def test_entries_copy(self, lookup_registry: ProfileLookupRegistry) -> None:
        """Mutating the returned list does not affect internal state."""
        entries1 = lookup_registry.get_entries("bearer_technology")
        original_len = len(entries1)
        entries1.clear()

        entries2 = lookup_registry.get_entries("bearer_technology")
        assert len(entries2) == original_len
