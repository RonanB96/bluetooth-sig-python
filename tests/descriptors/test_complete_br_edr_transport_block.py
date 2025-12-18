"""Tests for Complete BR-EDR Transport Block Data descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import CompleteBREDRTransportBlockDataDescriptor
from bluetooth_sig.gatt.descriptors.complete_br_edr_transport_block_data import CompleteBREDRTransportBlockDataData


class TestCompleteBREDRTransportBlockDataDescriptor:
    """Test Complete BR-EDR Transport Block Data descriptor functionality."""

    def test_parse_complete_br_edr_transport_block_data(self) -> None:
        """Test parsing complete BR-EDR transport block data."""
        cbtbd = CompleteBREDRTransportBlockDataDescriptor()
        # Simple test data - actual format is complex
        data = b"\x01\x02\x03\x04"

        result = cbtbd.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, CompleteBREDRTransportBlockDataData)
        # Note: This descriptor has a complex format, so we're just testing basic parsing

    def test_uuid_resolution(self) -> None:
        """Test that Complete BR-EDR Transport Block Data has correct UUID."""
        cbtbd = CompleteBREDRTransportBlockDataDescriptor()
        assert str(cbtbd.uuid) == "0000290F-0000-1000-8000-00805F9B34FB"
