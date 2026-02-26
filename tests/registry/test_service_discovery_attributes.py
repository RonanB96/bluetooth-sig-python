"""Tests for Service Discovery Attribute ID Registry."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.service_discovery.attribute_ids import (
    ServiceDiscoveryAttributeRegistry,
)
from bluetooth_sig.types.registry.profile_types import (
    AttributeIdEntry,
    ProtocolParameterEntry,
)


@pytest.fixture(scope="session")
def sd_registry() -> ServiceDiscoveryAttributeRegistry:
    """Create a service discovery attribute registry once per test session."""
    return ServiceDiscoveryAttributeRegistry()


class TestServiceDiscoveryAttributeRegistryInit:
    """Initialisation and lazy-loading tests."""

    def test_registry_initialization(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Registry creates without error."""
        assert isinstance(sd_registry, ServiceDiscoveryAttributeRegistry)

    def test_lazy_loading(self) -> None:
        """Data is not loaded until first query."""
        reg = ServiceDiscoveryAttributeRegistry()
        assert not reg._loaded

        _ = reg.get_all_categories()
        assert reg._loaded


class TestAttributeIdLoading:
    """Tests that validate YAML data is loaded correctly."""

    def test_categories_loaded(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """At least the known attribute_ids files are loaded."""
        cats = sd_registry.get_all_categories()
        assert len(cats) >= 20
        # Key categories from the YAML tree
        assert "universal_attributes" in cats
        assert "sdp" in cats
        assert "a2dp" in cats
        assert "attribute_id_offsets_for_strings" in cats

    def test_universal_attributes_entries(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """universal_attributes should have well-known SDP entries."""
        entries = sd_registry.get_attribute_ids("universal_attributes")
        assert len(entries) >= 10
        assert all(isinstance(e, AttributeIdEntry) for e in entries)

        names = {e.name for e in entries}
        assert "ServiceRecordHandle" in names
        assert "ServiceClassIDList" in names

    def test_entry_values_are_ints(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """All loaded values should be integers, not hex strings."""
        for cat in sd_registry.get_all_categories():
            for entry in sd_registry.get_attribute_ids(cat):
                assert isinstance(entry.value, int), f"{cat}/{entry.name}: value is not int"

    def test_attribute_id_offsets_loaded(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """attribute_id_offsets_for_strings.yaml should load as its own category."""
        entries = sd_registry.get_attribute_ids("attribute_id_offsets_for_strings")
        assert len(entries) >= 3
        names = {e.name for e in entries}
        assert "ServiceName" in names

    def test_unknown_category_returns_empty(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Querying a non-existent category returns an empty list."""
        assert sd_registry.get_attribute_ids("nonexistent_profile") == []


class TestProtocolParameters:
    """Tests for protocol_parameters.yaml loading."""

    def test_protocol_parameters_loaded(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """protocol_parameters should have at least L2CAP and RFCOMM entries."""
        params = sd_registry.get_protocol_parameters()
        assert len(params) >= 4
        assert all(isinstance(p, ProtocolParameterEntry) for p in params)

        protocols = {p.protocol for p in params}
        assert "L2CAP" in protocols
        assert "RFCOMM" in protocols

    def test_protocol_parameter_fields(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Each entry has non-empty protocol, name, and a valid index."""
        for p in sd_registry.get_protocol_parameters():
            assert p.protocol
            assert p.name
            assert isinstance(p.index, int)


class TestResolveAttributeName:
    """Tests for the resolve_attribute_name convenience method."""

    def test_resolve_known_attribute(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Resolving a known value returns the correct name."""
        name = sd_registry.resolve_attribute_name("universal_attributes", 0x0001)
        assert name == "ServiceClassIDList"

    def test_resolve_unknown_value(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Resolving an unknown value returns None."""
        assert sd_registry.resolve_attribute_name("universal_attributes", 0xFFFF) is None

    def test_resolve_unknown_category(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Resolving in an unknown category returns None."""
        assert sd_registry.resolve_attribute_name("nonexistent_profile", 0x0000) is None


class TestReturnedListsAreDefensiveCopies:
    """Mutations on returned lists must not affect registry state."""

    def test_attribute_ids_copy(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Mutating the returned list does not affect internal state."""
        entries1 = sd_registry.get_attribute_ids("universal_attributes")
        original_len = len(entries1)
        entries1.clear()

        entries2 = sd_registry.get_attribute_ids("universal_attributes")
        assert len(entries2) == original_len

    def test_protocol_params_copy(self, sd_registry: ServiceDiscoveryAttributeRegistry) -> None:
        """Mutating the returned protocol parameters list is safe."""
        params1 = sd_registry.get_protocol_parameters()
        original_len = len(params1)
        params1.clear()

        params2 = sd_registry.get_protocol_parameters()
        assert len(params2) == original_len
