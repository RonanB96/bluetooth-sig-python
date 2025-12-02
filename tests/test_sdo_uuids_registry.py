"""Tests for SDO UUIDs registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.uuids.sdo_uuids import SdoUuidsRegistry
from bluetooth_sig.types.registry.sdo_uuids import SdoUuidInfo as SdoInfo
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def sdo_uuids_registry() -> SdoUuidsRegistry:
    """Create a SDO UUIDs registry once per test session."""
    return SdoUuidsRegistry()


class TestSdoUuidsRegistry:
    """Test the SdoUuidsRegistry class."""

    def test_registry_initialization(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(sdo_uuids_registry, SdoUuidsRegistry)
        # Should have loaded some SDO UUIDs if YAML exists
        sdo_uuids = sdo_uuids_registry.get_all_sdo_uuids()
        assert isinstance(sdo_uuids, list)
        # If submodule is initialized, should have SDO UUIDs
        if sdo_uuids:
            assert all(isinstance(sdo, SdoInfo) for sdo in sdo_uuids)

    def test_get_sdo_info(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test lookup by UUID string."""
        # Test with a known SDO UUID (Wireless Power Transfer)
        info = sdo_uuids_registry.get_sdo_info("0xFFFE")
        if info:  # Only if YAML loaded
            assert isinstance(info, SdoInfo)
            assert info.name == "Wireless Power Transfer"

    def test_get_sdo_info_by_name(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test lookup by SDO name."""
        # Test with known SDO name (Wireless Power Transfer)
        info = sdo_uuids_registry.get_sdo_info_by_name("Wireless Power Transfer")
        if info:  # Only if YAML loaded
            assert isinstance(info, SdoInfo)
            assert info.name == "Wireless Power Transfer"
            assert info.uuid.short_form.upper() == "FFFE"

        # Test case insensitive
        info_lower = sdo_uuids_registry.get_sdo_info_by_name("wireless power transfer")
        assert info_lower == info

        # Test not found
        info_none = sdo_uuids_registry.get_sdo_info_by_name("Nonexistent SDO")
        assert info_none is None

    def test_get_sdo_info_by_id(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test lookup by SDO ID."""
        # Test with known SDO ID
        info = sdo_uuids_registry.get_sdo_info_by_id("org.bluetooth.sdo.wireless_power_transfer")
        if info:  # Only if YAML loaded
            assert isinstance(info, SdoInfo)
            assert info.name == "Wireless Power Transfer"
            assert info.uuid.short_form.upper() == "FFFE"

        # Test not found
        info_none = sdo_uuids_registry.get_sdo_info_by_id("org.bluetooth.sdo.nonexistent")
        assert info_none is None

    def test_get_sdo_info_by_bluetooth_uuid(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for a known SDO
        bt_uuid = BluetoothUUID("FFFE")
        info = sdo_uuids_registry.get_sdo_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, SdoInfo)
            assert info.name == "Wireless Power Transfer"

    def test_get_sdo_info_not_found(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test lookup for non-existent SDO."""
        info = sdo_uuids_registry.get_sdo_info("nonexistent")
        assert info is None

        info = sdo_uuids_registry.get_sdo_info("0x0000")  # Not an SDO UUID
        assert info is None

    def test_is_sdo_uuid(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test SDO UUID validation."""
        # Known SDO UUID
        has_sdos = bool(sdo_uuids_registry.get_all_sdo_uuids())
        assert sdo_uuids_registry.is_sdo_uuid("0xFFFE") or not has_sdos

        # Non-SDO UUID
        assert not sdo_uuids_registry.is_sdo_uuid("0x0000")

        # Invalid UUID
        assert not sdo_uuids_registry.is_sdo_uuid("invalid")

    def test_get_all_sdo_uuids(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test getting all SDO UUIDs."""
        sdo_uuids = sdo_uuids_registry.get_all_sdo_uuids()
        assert isinstance(sdo_uuids, list)

        if sdo_uuids:
            # If loaded, check structure
            for sdo in sdo_uuids:
                assert isinstance(sdo, SdoInfo)
                assert isinstance(sdo.name, str)
                assert isinstance(sdo.uuid, BluetoothUUID)
                # Should be 16-bit UUIDs
                assert len(sdo.uuid.short_form) == 4

    def test_sdo_info_structure(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test SdoInfo dataclass structure."""
        sdo_uuids = sdo_uuids_registry.get_all_sdo_uuids()
        if sdo_uuids:
            sdo = sdo_uuids[0]
            assert hasattr(sdo, "uuid")
            assert hasattr(sdo, "name")
            assert hasattr(sdo, "id")
            assert isinstance(sdo.uuid, BluetoothUUID)
            assert isinstance(sdo.name, str)

    def test_uuid_formats(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | BluetoothUUID] = ["FFFE", "0xFFFE", "0XFFFE", BluetoothUUID("FFFE")]
        for fmt in formats:
            info = sdo_uuids_registry.get_sdo_info(fmt)
            if sdo_uuids_registry.is_sdo_uuid("FFFE"):
                assert info is not None
                assert info.name == "Wireless Power Transfer"

    def test_normalize_name_for_id(self, sdo_uuids_registry: SdoUuidsRegistry) -> None:
        """Test name normalization for ID generation."""
        # Test various name formats
        test_cases = [
            ("Wireless Power Transfer", "wireless_power_transfer"),
            ("Car Connectivity Consortium, LLC", "car_connectivity_consortium_llc"),
            ("FiRa Consortium", "fira_consortium"),
            ("Mopria Alliance BLE", "mopria_alliance_ble"),
            ("FIDO2 secure client-to-authenticator transport", "fido2_secure_client_to_authenticator_transport"),
        ]

        for name, expected_suffix in test_cases:
            normalized = sdo_uuids_registry._normalize_name_for_id(name)
            assert normalized == expected_suffix
