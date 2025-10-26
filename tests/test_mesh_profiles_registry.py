"""Tests for mesh profiles registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.mesh_profiles import MeshProfileInfo, MeshProfilesRegistry
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def mesh_profiles_registry() -> MeshProfilesRegistry:
    """Create a mesh profiles registry once per test session."""
    return MeshProfilesRegistry()


class TestMeshProfilesRegistry:
    """Test the MeshProfilesRegistry class."""

    def test_registry_initialization(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(mesh_profiles_registry, MeshProfilesRegistry)
        # Should have loaded some mesh profiles if YAML exists
        mesh_profiles = mesh_profiles_registry.get_all_mesh_profiles()
        assert isinstance(mesh_profiles, list)
        # If submodule is initialized, should have mesh profiles
        if mesh_profiles:
            assert all(isinstance(mp, MeshProfileInfo) for mp in mesh_profiles)

    def test_get_mesh_profile_info(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known mesh profile UUID (Generic OnOff Server)
        info = mesh_profiles_registry.get_mesh_profile_info("0x1000")
        if info:  # Only if YAML loaded
            assert isinstance(info, MeshProfileInfo)
            assert info.name == "Generic OnOff Server"
            assert info.id == "org.bluetooth.mesh.model.generic_on_off_server"

    def test_get_mesh_profile_info_by_name(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test lookup by mesh profile name."""
        # Test with known mesh profile name (Generic OnOff Server)
        info = mesh_profiles_registry.get_mesh_profile_info_by_name("Generic OnOff Server")
        if info:  # Only if YAML loaded
            assert isinstance(info, MeshProfileInfo)
            assert info.name == "Generic OnOff Server"
            assert info.uuid.short_form.upper() == "1000"

        # Test case insensitive
        info_lower = mesh_profiles_registry.get_mesh_profile_info_by_name("generic onoff server")
        assert info_lower == info

        # Test not found
        info_none = mesh_profiles_registry.get_mesh_profile_info_by_name("Nonexistent Mesh Profile")
        assert info_none is None

    def test_get_mesh_profile_info_by_id(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test lookup by mesh profile ID."""
        # Test with known mesh profile ID
        info = mesh_profiles_registry.get_mesh_profile_info_by_id("org.bluetooth.mesh.model.generic_on_off_server")
        if info:  # Only if YAML loaded
            assert isinstance(info, MeshProfileInfo)
            assert info.name == "Generic OnOff Server"
            assert info.uuid.short_form.upper() == "1000"

        # Test not found
        info_none = mesh_profiles_registry.get_mesh_profile_info_by_id("org.bluetooth.mesh.model.nonexistent")
        assert info_none is None

    def test_get_mesh_profile_info_by_bluetooth_uuid(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known mesh profile
        bt_uuid = BluetoothUUID("1000")
        info = mesh_profiles_registry.get_mesh_profile_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, MeshProfileInfo)
            assert info.name == "Generic OnOff Server"

    def test_get_mesh_profile_info_not_found(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test lookup for non-existent mesh profile."""
        info = mesh_profiles_registry.get_mesh_profile_info("nonexistent")
        assert info is None

        info = mesh_profiles_registry.get_mesh_profile_info("0x0000")  # Not a mesh profile UUID
        assert info is None

    def test_is_mesh_profile_uuid(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test mesh profile UUID validation."""
        # Known mesh profile UUID
        has_profiles = bool(mesh_profiles_registry.get_all_mesh_profiles())
        assert mesh_profiles_registry.is_mesh_profile_uuid("0x1000") or not has_profiles

        # Non-mesh profile UUID
        assert not mesh_profiles_registry.is_mesh_profile_uuid("0x0000")

        # Invalid UUID
        assert not mesh_profiles_registry.is_mesh_profile_uuid("invalid")

    def test_get_all_mesh_profiles(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test getting all mesh profiles."""
        mesh_profiles = mesh_profiles_registry.get_all_mesh_profiles()
        assert isinstance(mesh_profiles, list)

        if mesh_profiles:
            # If loaded, check structure
            for mesh_profile in mesh_profiles:
                assert isinstance(mesh_profile, MeshProfileInfo)
                assert isinstance(mesh_profile.name, str)
                assert isinstance(mesh_profile.uuid, BluetoothUUID)
                assert isinstance(mesh_profile.id, str)
                # Should be 16-bit UUIDs
                assert len(mesh_profile.uuid.short_form) == 4

    def test_mesh_profile_info_structure(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test MeshProfileInfo dataclass structure."""
        mesh_profiles = mesh_profiles_registry.get_all_mesh_profiles()
        if mesh_profiles:
            mesh_profile = mesh_profiles[0]
            assert hasattr(mesh_profile, "uuid")
            assert hasattr(mesh_profile, "name")
            assert hasattr(mesh_profile, "id")
            assert isinstance(mesh_profile.uuid, BluetoothUUID)
            assert isinstance(mesh_profile.name, str)
            assert isinstance(mesh_profile.id, str)

    def test_uuid_formats(self, mesh_profiles_registry: MeshProfilesRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | int] = ["1000", "0x1000", "0X1000", 0x1000]
        for fmt in formats:
            info = mesh_profiles_registry.get_mesh_profile_info(fmt)
            if mesh_profiles_registry.is_mesh_profile_uuid("1000"):
                assert info is not None
                assert info.name == "Generic OnOff Server"
