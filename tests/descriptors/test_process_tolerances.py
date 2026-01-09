"""Tests for Process Tolerances descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ProcessTolerancesDescriptor
from bluetooth_sig.gatt.descriptors.process_tolerances import ProcessTolerancesData


class TestProcessTolerancesDescriptor:
    """Test Process Tolerances descriptor functionality."""

    def test_parse_process_tolerances(self) -> None:
        """Test parsing process tolerances."""
        pt = ProcessTolerancesDescriptor()
        # Tolerance: 0x00000001
        data = b"\x01\x00\x00\x00"

        result = pt.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, ProcessTolerancesData)
        assert result.value.tolerance_min == 0x0001
        assert result.value.tolerance_max == 0x0000

    def test_parse_invalid_length(self) -> None:
        """Test parsing process tolerances with invalid length."""
        pt = ProcessTolerancesDescriptor()
        data = b"\x01\x00\x00"  # Too short

        result = pt.parse_value(data)
        assert result.parse_success is False
        assert "Process Tolerances data expected 4 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Process Tolerances has correct UUID."""
        pt = ProcessTolerancesDescriptor()
        assert str(pt.uuid) == "00002914-0000-1000-8000-00805F9B34FB"
