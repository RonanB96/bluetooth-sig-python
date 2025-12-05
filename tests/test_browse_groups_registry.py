"""Tests for browse groups registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.uuids.browse_groups import BrowseGroupsRegistry
from bluetooth_sig.types.registry.browse_group_identifiers import BrowseGroupInfo
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def browse_groups_registry() -> BrowseGroupsRegistry:
    """Create a browse groups registry once per test session."""
    return BrowseGroupsRegistry()


class TestBrowseGroupsRegistry:
    """Test the BrowseGroupsRegistry class."""

    def test_registry_initialization(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(browse_groups_registry, BrowseGroupsRegistry)
        # Should have loaded some browse groups if YAML exists
        browse_groups = browse_groups_registry.get_all_browse_groups()
        assert isinstance(browse_groups, list)
        # If submodule is initialized, should have browse groups
        if browse_groups:
            assert all(isinstance(bg, BrowseGroupInfo) for bg in browse_groups)

    def test_get_browse_group_info(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known browse group UUID (PublicBrowseRoot)
        info = browse_groups_registry.get_browse_group_info("0x1002")
        if info:  # Only if YAML loaded
            assert isinstance(info, BrowseGroupInfo)
            assert info.name == "PublicBrowseRoot"
            assert info.id == "org.bluetooth.browse_group.public_browse_root"

    def test_get_browse_group_info_by_name(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test lookup by browse group name."""
        # Test with known browse group name (PublicBrowseRoot)
        info = browse_groups_registry.get_browse_group_info_by_name("PublicBrowseRoot")
        if info:  # Only if YAML loaded
            assert isinstance(info, BrowseGroupInfo)
            assert info.name == "PublicBrowseRoot"
            assert info.uuid.short_form.upper() == "1002"

        # Test case insensitive
        info_lower = browse_groups_registry.get_browse_group_info_by_name("publicbrowseroot")
        assert info_lower == info

        # Test not found
        info_none = browse_groups_registry.get_browse_group_info_by_name("Nonexistent Browse Group")
        assert info_none is None

    def test_get_browse_group_info_by_id(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test lookup by browse group ID."""
        # Test with known browse group ID
        info = browse_groups_registry.get_browse_group_info_by_id("org.bluetooth.browse_group.public_browse_root")
        if info:  # Only if YAML loaded
            assert isinstance(info, BrowseGroupInfo)
            assert info.name == "PublicBrowseRoot"
            assert info.uuid.short_form.upper() == "1002"

        # Test not found
        info_none = browse_groups_registry.get_browse_group_info_by_id("org.bluetooth.browse_group.nonexistent")
        assert info_none is None

    def test_get_browse_group_info_by_bluetooth_uuid(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known browse group
        bt_uuid = BluetoothUUID("1002")
        info = browse_groups_registry.get_browse_group_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, BrowseGroupInfo)
            assert info.name == "PublicBrowseRoot"

    def test_get_browse_group_info_not_found(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test lookup for non-existent browse group."""
        info = browse_groups_registry.get_browse_group_info("nonexistent")
        assert info is None

        info = browse_groups_registry.get_browse_group_info("0x0000")  # Not a browse group UUID
        assert info is None

    def test_is_browse_group_uuid(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test browse group UUID validation."""
        # Known browse group UUID
        has_groups = bool(browse_groups_registry.get_all_browse_groups())
        assert browse_groups_registry.is_browse_group_uuid("0x1002") or not has_groups

        # Non-browse group UUID
        assert not browse_groups_registry.is_browse_group_uuid("0x0000")

        # Invalid UUID
        assert not browse_groups_registry.is_browse_group_uuid("invalid")

    def test_get_all_browse_groups(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test getting all browse groups."""
        browse_groups = browse_groups_registry.get_all_browse_groups()
        assert isinstance(browse_groups, list)

        if browse_groups:
            # If loaded, check structure
            for browse_group in browse_groups:
                assert isinstance(browse_group, BrowseGroupInfo)
                assert isinstance(browse_group.name, str)
                assert isinstance(browse_group.uuid, BluetoothUUID)
                assert isinstance(browse_group.id, str)
                # Should be 16-bit UUIDs
                assert len(browse_group.uuid.short_form) == 4

    def test_browse_group_info_structure(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test BrowseGroupInfo dataclass structure."""
        browse_groups = browse_groups_registry.get_all_browse_groups()
        if browse_groups:
            browse_group = browse_groups[0]
            assert hasattr(browse_group, "uuid")
            assert hasattr(browse_group, "name")
            assert hasattr(browse_group, "id")
            assert isinstance(browse_group.uuid, BluetoothUUID)
            assert isinstance(browse_group.name, str)
            assert isinstance(browse_group.id, str)

    def test_uuid_formats(self, browse_groups_registry: BrowseGroupsRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | BluetoothUUID] = ["1002", "0x1002", "0X1002", BluetoothUUID("1002")]
        for fmt in formats:
            info = browse_groups_registry.get_browse_group_info(fmt)
            if browse_groups_registry.is_browse_group_uuid("1002"):
                assert info is not None
                assert info.name == "PublicBrowseRoot"
