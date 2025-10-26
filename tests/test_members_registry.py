"""Tests for members registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.members import MemberInfo, MembersRegistry
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def members_registry() -> MembersRegistry:
    """Create a members registry once per test session."""
    return MembersRegistry()


class TestMembersRegistry:
    """Test the MembersRegistry class."""

    def test_registry_initialization(self, members_registry: MembersRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(members_registry, MembersRegistry)
        # Should have loaded some members if YAML exists
        members = members_registry.get_all_members()
        assert isinstance(members, list)
        # If submodule is initialized, should have members
        if members:
            assert all(isinstance(m, MemberInfo) for m in members)

    def test_get_member_info_by_uuid(self, members_registry: MembersRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known member UUID (GN Netcom)
        name = members_registry.get_member_name("0xFEFF")
        if name:  # Only if YAML loaded
            assert isinstance(name, str)
            assert name == "GN Netcom"

    def test_get_member_info_by_name(self, members_registry: MembersRegistry) -> None:
        """Test lookup by company name."""
        # Test with known member name (GN Netcom)
        info = members_registry.get_member_info_by_name("GN Netcom")
        if info:  # Only if YAML loaded
            assert isinstance(info, MemberInfo)
            assert info.name == "GN Netcom"
            assert info.uuid.short_form.upper() == "FEFF"

        # Test case insensitive
        info_lower = members_registry.get_member_info_by_name("gn netcom")
        assert info_lower == info

        # Test not found
        info_none = members_registry.get_member_info_by_name("Nonexistent Company")
        assert info_none is None

    def test_get_member_info_by_bluetooth_uuid(self, members_registry: MembersRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known member
        bt_uuid = BluetoothUUID("FEFF")
        name = members_registry.get_member_name(bt_uuid)
        if name:  # Only if YAML loaded
            assert isinstance(name, str)
            assert name == "GN Netcom"

    def test_get_member_info_not_found(self, members_registry: MembersRegistry) -> None:
        """Test lookup for non-existent member."""
        name = members_registry.get_member_name("nonexistent")
        assert name is None

        name = members_registry.get_member_name("0x0000")  # Not a member UUID
        assert name is None

    def test_is_member_uuid(self, members_registry: MembersRegistry) -> None:
        """Test member UUID validation."""
        # Known member UUID
        assert members_registry.is_member_uuid("0xFEFF") or not members_registry.get_all_members()

        # Non-member UUID
        assert not members_registry.is_member_uuid("0x0000")

        # Invalid UUID
        assert not members_registry.is_member_uuid("invalid")

    def test_get_all_members(self, members_registry: MembersRegistry) -> None:
        """Test getting all members."""
        members = members_registry.get_all_members()
        assert isinstance(members, list)

        if members:
            # If loaded, check structure
            for member in members:
                assert isinstance(member, MemberInfo)
                assert isinstance(member.name, str)
                assert isinstance(member.uuid, BluetoothUUID)
                # Should be 16-bit UUIDs
                assert len(member.uuid.short_form) == 4

    def test_member_info_structure(self, members_registry: MembersRegistry) -> None:
        """Test MemberInfo dataclass structure."""
        members = members_registry.get_all_members()
        if members:
            member = members[0]
            assert hasattr(member, "uuid")
            assert hasattr(member, "name")
            assert isinstance(member.uuid, BluetoothUUID)
            assert isinstance(member.name, str)

    def test_uuid_formats(self, members_registry: MembersRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | int] = ["FEFF", "0xFEFF", "0XFEFF", 0xFEFF]
        for fmt in formats:
            name = members_registry.get_member_name(fmt)
            if members_registry.is_member_uuid("FEFF"):
                assert name == "GN Netcom"
