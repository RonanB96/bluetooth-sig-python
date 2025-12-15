"""Tests for base descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CCCDDescriptor


class TestBaseDescriptor:
    """Test base descriptor functionality."""

    def test_uuid_resolution(self) -> None:
        """Test that descriptors resolve their UUID correctly."""
        cccd = CCCDDescriptor()
        assert cccd.uuid is not None
        assert "2902" in str(cccd.uuid)

    def test_info_property(self) -> None:
        """Test descriptor info property."""
        cccd = CCCDDescriptor()
        info = cccd.info
        assert info.name == "Client Characteristic Configuration"
        assert "2902" in str(info.uuid)
