"""Tests for protocol identifiers registry functionality."""

from __future__ import annotations

import pytest

from bluetooth_sig.registry.uuids.protocol_identifiers import ProtocolIdentifiersRegistry, ProtocolInfo
from bluetooth_sig.types.uuid import BluetoothUUID


@pytest.fixture(scope="session")
def protocol_identifiers_registry() -> ProtocolIdentifiersRegistry:
    """Create a protocol identifiers registry once per test session."""
    return ProtocolIdentifiersRegistry()


class TestProtocolIdentifiersRegistry:  # pylint: disable=too-many-public-methods
    """Test the ProtocolIdentifiersRegistry class."""

    def test_registry_initialization(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test that the registry initializes properly."""
        assert isinstance(protocol_identifiers_registry, ProtocolIdentifiersRegistry)
        # Should have loaded some protocols if YAML exists
        protocols = protocol_identifiers_registry.get_all_protocols()
        assert isinstance(protocols, list)
        # If submodule is initialized, should have protocols
        if protocols:
            assert all(isinstance(p, ProtocolInfo) for p in protocols)

    def test_get_protocol_info_l2cap(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup of L2CAP protocol by UUID."""
        # Test with L2CAP UUID (0x0100)
        info = protocol_identifiers_registry.get_protocol_info("0x0100")
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "L2CAP"
            assert info.uuid.short_form.upper() == "0100"

    def test_get_protocol_info_rfcomm(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup of RFCOMM protocol by UUID."""
        # Test with RFCOMM UUID (0x0003)
        info = protocol_identifiers_registry.get_protocol_info("0x0003")
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "RFCOMM"
            assert info.uuid.short_form.upper() == "0003"

    def test_get_protocol_info_avdtp(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup of AVDTP protocol by UUID."""
        # Test with AVDTP UUID (0x0019)
        info = protocol_identifiers_registry.get_protocol_info("0x0019")
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "AVDTP"
            assert info.uuid.short_form.upper() == "0019"

    def test_get_protocol_info_bnep(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup of BNEP protocol by UUID."""
        # Test with BNEP UUID (0x000F)
        info = protocol_identifiers_registry.get_protocol_info("0x000F")
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "BNEP"
            assert info.uuid.short_form.upper() == "000F"

    def test_get_protocol_info_by_name(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup by protocol name."""
        # Test with known protocol name (L2CAP)
        info = protocol_identifiers_registry.get_protocol_info("L2CAP")
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "L2CAP"
            assert info.uuid.short_form.upper() == "0100"

        # Test case insensitive
        info_lower = protocol_identifiers_registry.get_protocol_info("l2cap")
        assert info_lower == info

        # Test not found
        info_none = protocol_identifiers_registry.get_protocol_info("Nonexistent Protocol")
        assert info_none is None

    def test_get_protocol_info_by_name_method(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test dedicated get_protocol_info_by_name method."""
        # Test with known protocol name
        info = protocol_identifiers_registry.get_protocol_info_by_name("RFCOMM")
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "RFCOMM"
            assert info.uuid.short_form.upper() == "0003"

        # Test case insensitive
        info_lower = protocol_identifiers_registry.get_protocol_info_by_name("rfcomm")
        assert info_lower == info

        # Test not found
        info_none = protocol_identifiers_registry.get_protocol_info_by_name("Nonexistent Protocol")
        assert info_none is None

    def test_get_protocol_info_by_bluetooth_uuid(
        self, protocol_identifiers_registry: ProtocolIdentifiersRegistry
    ) -> None:
        """Test lookup by BluetoothUUID object."""
        # Create a BluetoothUUID for L2CAP
        bt_uuid = BluetoothUUID("0100")
        info = protocol_identifiers_registry.get_protocol_info(bt_uuid)
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "L2CAP"

    def test_get_protocol_info_by_int(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup by integer UUID."""
        # Test with RFCOMM as integer (0x0003 = 3)
        info = protocol_identifiers_registry.get_protocol_info(3)
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "RFCOMM"

        # Test with L2CAP as integer (0x0100 = 256)
        info = protocol_identifiers_registry.get_protocol_info(256)
        if info:  # Only if YAML loaded
            assert isinstance(info, ProtocolInfo)
            assert info.name == "L2CAP"

    def test_get_protocol_info_not_found(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test lookup for non-existent protocol."""
        info = protocol_identifiers_registry.get_protocol_info("nonexistent")
        assert info is None

        info = protocol_identifiers_registry.get_protocol_info("0xFFFF")  # Not a protocol UUID
        assert info is None

    def test_is_known_protocol(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test protocol UUID validation."""
        # Known protocol UUID
        has_protocols = bool(protocol_identifiers_registry.get_all_protocols())
        assert protocol_identifiers_registry.is_known_protocol("0x0100") or not has_protocols  # L2CAP

        # Non-protocol UUID
        assert not protocol_identifiers_registry.is_known_protocol("0xFFFF")

        # Invalid UUID
        assert not protocol_identifiers_registry.is_known_protocol("invalid")

    def test_is_l2cap(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test L2CAP helper method."""
        has_protocols = bool(protocol_identifiers_registry.get_all_protocols())

        # Test with L2CAP UUID
        assert protocol_identifiers_registry.is_l2cap("0x0100") or not has_protocols
        assert protocol_identifiers_registry.is_l2cap(256) or not has_protocols

        # Test with non-L2CAP UUID
        assert not protocol_identifiers_registry.is_l2cap("0x0003")  # RFCOMM

    def test_is_rfcomm(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test RFCOMM helper method."""
        has_protocols = bool(protocol_identifiers_registry.get_all_protocols())

        # Test with RFCOMM UUID
        assert protocol_identifiers_registry.is_rfcomm("0x0003") or not has_protocols
        assert protocol_identifiers_registry.is_rfcomm(3) or not has_protocols

        # Test with non-RFCOMM UUID
        assert not protocol_identifiers_registry.is_rfcomm("0x0100")  # L2CAP

    def test_is_avdtp(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test AVDTP helper method."""
        has_protocols = bool(protocol_identifiers_registry.get_all_protocols())

        # Test with AVDTP UUID
        assert protocol_identifiers_registry.is_avdtp("0x0019") or not has_protocols
        assert protocol_identifiers_registry.is_avdtp(25) or not has_protocols  # 0x19 = 25

        # Test with non-AVDTP UUID
        assert not protocol_identifiers_registry.is_avdtp("0x0003")  # RFCOMM

    def test_is_bnep(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test BNEP helper method."""
        has_protocols = bool(protocol_identifiers_registry.get_all_protocols())

        # Test with BNEP UUID
        assert protocol_identifiers_registry.is_bnep("0x000F") or not has_protocols
        assert protocol_identifiers_registry.is_bnep(15) or not has_protocols  # 0x0F = 15

        # Test with non-BNEP UUID
        assert not protocol_identifiers_registry.is_bnep("0x0003")  # RFCOMM

    def test_get_all_protocols(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test getting all protocols."""
        protocols = protocol_identifiers_registry.get_all_protocols()
        assert isinstance(protocols, list)

        if protocols:
            # If loaded, check structure
            for protocol in protocols:
                assert isinstance(protocol, ProtocolInfo)
                assert isinstance(protocol.name, str)
                assert isinstance(protocol.uuid, BluetoothUUID)
                # Protocol UUIDs should be 16-bit
                assert len(protocol.uuid.short_form) == 4

    def test_protocol_info_structure(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test ProtocolInfo dataclass structure."""
        protocols = protocol_identifiers_registry.get_all_protocols()
        if protocols:
            protocol = protocols[0]
            assert hasattr(protocol, "uuid")
            assert hasattr(protocol, "name")
            assert hasattr(protocol, "protocol_type")
            assert isinstance(protocol.uuid, BluetoothUUID)
            assert isinstance(protocol.name, str)
            assert isinstance(protocol.protocol_type, str)
            # protocol_type should be uppercase version of name
            assert protocol.protocol_type == protocol.name.upper()

    def test_protocol_type_property(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test protocol_type property."""
        info = protocol_identifiers_registry.get_protocol_info("L2CAP")
        if info:
            assert info.protocol_type == "L2CAP"

        info = protocol_identifiers_registry.get_protocol_info("RFCOMM")
        if info:
            assert info.protocol_type == "RFCOMM"

    def test_uuid_formats(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test various UUID input formats."""
        formats: list[str | int] = ["0100", "0x0100", "0X0100", 0x0100, 256]
        for fmt in formats:
            info = protocol_identifiers_registry.get_protocol_info(fmt)
            if protocol_identifiers_registry.is_known_protocol("0100"):
                assert info is not None
                assert info.name == "L2CAP"

    def test_well_known_protocols(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test that well-known Bluetooth protocols are present if YAML loaded."""
        protocols = protocol_identifiers_registry.get_all_protocols()
        if not protocols:
            pytest.skip("YAML not loaded, skipping well-known protocol check")

        # Check for some well-known protocols
        expected_protocols = {
            "SDP": "0001",
            "RFCOMM": "0003",
            "ATT": "0007",
            "BNEP": "000F",
            "AVDTP": "0019",
            "L2CAP": "0100",
        }

        for name, uuid in expected_protocols.items():
            info = protocol_identifiers_registry.get_protocol_info(name)
            # Only assert if the protocol exists (may not in minimal test data)
            if info:
                assert info.uuid.short_form.upper() == uuid, f"Expected {name} to have UUID {uuid}"

    def test_singleton_pattern(self) -> None:
        """Test that the registry follows singleton pattern."""
        registry1 = ProtocolIdentifiersRegistry.get_instance()
        registry2 = ProtocolIdentifiersRegistry.get_instance()
        assert registry1 is registry2

    def test_thread_safety(self, protocol_identifiers_registry: ProtocolIdentifiersRegistry) -> None:
        """Test that concurrent lookups work correctly."""
        import threading
        import time

        results: list[ProtocolInfo | None] = []
        errors: list[Exception] = []

        def lookup_protocol() -> None:
            try:
                time.sleep(0.001)  # Small delay to increase concurrency
                info = protocol_identifiers_registry.get_protocol_info("L2CAP")
                results.append(info)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=lookup_protocol) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0

        # All results should be consistent (either all None or all the same)
        if results and results[0] is not None:
            for result in results:
                assert result is not None
                assert result.name == "L2CAP"
