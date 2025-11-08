"""Test registry import paths after restructuring."""

from __future__ import annotations

import pytest


class TestRegistryImportPaths:
    """Test that registry modules can be imported from new paths."""

    def test_backward_compatible_imports(self) -> None:
        """Test that old import paths still work via re-exports."""
        from bluetooth_sig.registry import (
            BaseRegistry,
            browse_groups_registry,
            declarations_registry,
            members_registry,
            mesh_profiles_registry,
            object_types_registry,
            sdo_uuids_registry,
            service_classes_registry,
            units_registry,
        )

        # Verify they're not None
        assert BaseRegistry is not None
        assert browse_groups_registry is not None
        assert declarations_registry is not None
        assert members_registry is not None
        assert mesh_profiles_registry is not None
        assert object_types_registry is not None
        assert sdo_uuids_registry is not None
        assert service_classes_registry is not None
        assert units_registry is not None

    def test_new_explicit_imports(self) -> None:
        """Test that new explicit import paths work."""
        from bluetooth_sig.registry.uuids import (
            browse_groups_registry,
            declarations_registry,
            members_registry,
            mesh_profiles_registry,
            object_types_registry,
            sdo_uuids_registry,
            service_classes_registry,
            units_registry,
        )

        # Verify they're not None
        assert browse_groups_registry is not None
        assert declarations_registry is not None
        assert members_registry is not None
        assert mesh_profiles_registry is not None
        assert object_types_registry is not None
        assert sdo_uuids_registry is not None
        assert service_classes_registry is not None
        assert units_registry is not None

    def test_individual_registry_imports(self) -> None:
        """Test that individual registry files can be imported."""
        from bluetooth_sig.registry.uuids.browse_groups import BrowseGroupsRegistry
        from bluetooth_sig.registry.uuids.declarations import DeclarationsRegistry
        from bluetooth_sig.registry.uuids.members import MembersRegistry
        from bluetooth_sig.registry.uuids.mesh_profiles import MeshProfilesRegistry
        from bluetooth_sig.registry.uuids.object_types import ObjectTypesRegistry
        from bluetooth_sig.registry.uuids.sdo_uuids import SdoUuidsRegistry
        from bluetooth_sig.registry.uuids.service_classes import ServiceClassesRegistry
        from bluetooth_sig.registry.uuids.units import UnitsRegistry

        # Verify they're not None
        assert BrowseGroupsRegistry is not None
        assert DeclarationsRegistry is not None
        assert MembersRegistry is not None
        assert MeshProfilesRegistry is not None
        assert ObjectTypesRegistry is not None
        assert SdoUuidsRegistry is not None
        assert ServiceClassesRegistry is not None
        assert UnitsRegistry is not None

    def test_subdirectory_init_imports(self) -> None:
        """Test that subdirectory __init__.py modules are importable."""
        # These should not raise ImportError even though they're currently empty
        import bluetooth_sig.registry.core
        import bluetooth_sig.registry.company_identifiers
        import bluetooth_sig.registry.service_discovery
        import bluetooth_sig.registry.profiles
        import bluetooth_sig.registry.uuids

        # Verify they're not None
        assert bluetooth_sig.registry.core is not None
        assert bluetooth_sig.registry.company_identifiers is not None
        assert bluetooth_sig.registry.service_discovery is not None
        assert bluetooth_sig.registry.profiles is not None
        assert bluetooth_sig.registry.uuids is not None
