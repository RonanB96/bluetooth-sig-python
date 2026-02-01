"""Tests for External Report Reference descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ExternalReportReferenceDescriptor
from bluetooth_sig.gatt.descriptors.external_report_reference import ExternalReportReferenceData


class TestExternalReportReferenceDescriptor:
    """Test External Report Reference descriptor functionality."""

    def test_parse_external_report_reference(self) -> None:
        """Test parsing external report reference."""
        err = ExternalReportReferenceDescriptor()
        data = b"\x01\x00"  # Report ID 1

        result = err.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, ExternalReportReferenceData)
        assert result.value.external_report_id == 0x0001

    def test_parse_invalid_length(self) -> None:
        """Test parsing external report reference with invalid length."""
        err = ExternalReportReferenceDescriptor()
        data = b"\x01"  # Too short (1 byte instead of 2)

        result = err.parse_value(data)
        assert result.parse_success is False
        assert "need 2 bytes, got 1" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that External Report Reference has correct UUID."""
        err = ExternalReportReferenceDescriptor()
        assert str(err.uuid) == "00002907-0000-1000-8000-00805F9B34FB"
