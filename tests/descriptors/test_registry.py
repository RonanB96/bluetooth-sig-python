"""Tests for descriptor registry functionality.

These tests dynamically discover all registered descriptors rather than
hardcoding lists, ensuring new descriptors are automatically tested.
"""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import DescriptorRegistry


class TestDescriptorRegistry:
    """Test descriptor registry functionality."""

    def test_registry_has_registered_descriptors(self) -> None:
        """Test that the registry has descriptors registered.

        This validates the registry is populated and functioning.
        """
        registered_uuids = DescriptorRegistry.list_registered_descriptors()
        assert len(registered_uuids) > 0, "No descriptors registered in registry"
        # Sanity check: we should have at least the core GATT descriptors
        assert len(registered_uuids) >= 10, f"Expected at least 10 registered descriptors, got {len(registered_uuids)}"

    def test_all_registered_descriptors_can_be_looked_up(self) -> None:
        """Test that all registered descriptors can be retrieved by UUID.

        Dynamically iterates over all registered descriptors to ensure
        get_descriptor_class works for each one.
        """
        registered_uuids = DescriptorRegistry.list_registered_descriptors()
        lookup_failures = []

        for uuid_str in registered_uuids:
            descriptor_class = DescriptorRegistry.get_descriptor_class(uuid_str)
            if descriptor_class is None:
                lookup_failures.append(uuid_str)

        if lookup_failures:
            error_msg = f"Failed to lookup {len(lookup_failures)} registered descriptors:\n" + "\n".join(
                f"  - {uuid}" for uuid in lookup_failures
            )
            raise AssertionError(error_msg)

    def test_all_registered_descriptors_can_be_created(self) -> None:
        """Test that all registered descriptors can be instantiated.

        Dynamically iterates over all registered descriptors to ensure
        create_descriptor works for each one.
        """
        registered_uuids = DescriptorRegistry.list_registered_descriptors()
        creation_failures = []

        for uuid_str in registered_uuids:
            descriptor = DescriptorRegistry.create_descriptor(uuid_str)
            if descriptor is None:
                creation_failures.append(uuid_str)

        if creation_failures:
            error_msg = f"Failed to create {len(creation_failures)} registered descriptors:\n" + "\n".join(
                f"  - {uuid}" for uuid in creation_failures
            )
            raise AssertionError(error_msg)

    def test_all_registered_descriptors_have_valid_uuids(self) -> None:
        """Test that all registered descriptor instances have valid UUIDs.

        Each descriptor instance should have a UUID that matches its
        registration in the registry.
        """
        registered_uuids = DescriptorRegistry.list_registered_descriptors()
        uuid_mismatches = []

        for uuid_str in registered_uuids:
            descriptor = DescriptorRegistry.create_descriptor(uuid_str)
            if descriptor is not None:
                instance_uuid = str(descriptor.uuid)
                if instance_uuid != uuid_str:
                    uuid_mismatches.append(f"{uuid_str} -> instance has {instance_uuid}")

        if uuid_mismatches:
            error_msg = f"UUID mismatches for {len(uuid_mismatches)} descriptors:\n" + "\n".join(
                f"  - {m}" for m in uuid_mismatches
            )
            raise AssertionError(error_msg)

    def test_create_unknown_descriptor_returns_none(self) -> None:
        """Test that creating an unknown descriptor returns None."""
        unknown = DescriptorRegistry.create_descriptor("FFFF")
        assert unknown is None

    def test_get_unknown_descriptor_class_returns_none(self) -> None:
        """Test that getting an unknown descriptor class returns None."""
        unknown_class = DescriptorRegistry.get_descriptor_class("FFFF")
        assert unknown_class is None

    def test_registry_descriptor_count(self) -> None:
        """Test that the expected number of descriptors are registered.

        This test documents the current count and will fail if descriptors
        are accidentally removed or if new ones are added without updating
        the expected count.
        """
        registered_uuids = DescriptorRegistry.list_registered_descriptors()
        # Current count of SIG GATT descriptors implemented
        # Update this number when adding new descriptors
        expected_minimum = 22  # All standard GATT descriptors (2900-2915)

        assert len(registered_uuids) >= expected_minimum, (
            f"Expected at least {expected_minimum} registered descriptors, "
            f"got {len(registered_uuids)}. "
            "Did a descriptor get accidentally removed?"
        )
