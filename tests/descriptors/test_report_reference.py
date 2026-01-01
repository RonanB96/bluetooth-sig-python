"""Tests for Report Reference descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ReportReferenceDescriptor
from bluetooth_sig.gatt.descriptors.report_reference import ReportReferenceData


class TestReportReferenceDescriptor:
    """Test Report Reference descriptor functionality."""

    def test_parse_report_reference(self) -> None:
        """Test parsing report reference."""
        rr = ReportReferenceDescriptor()
        data = b"\x01\x00"  # Report ID 1

        result = rr.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ReportReferenceData)
        assert result.value.report_id == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing report reference with invalid length."""
        rr = ReportReferenceDescriptor()
        data = b"\x01"  # Too short

        result = rr.parse_value(data)
        assert not result.parse_success
        assert "Report Reference data must be exactly 2 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Report Reference has correct UUID."""
        rr = ReportReferenceDescriptor()
        assert str(rr.uuid) == "00002908-0000-1000-8000-00805F9B34FB"
