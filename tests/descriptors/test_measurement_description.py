"""Tests for Measurement Description descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import MeasurementDescriptionDescriptor
from bluetooth_sig.gatt.descriptors.measurement_description import MeasurementDescriptionData


class TestMeasurementDescriptionDescriptor:
    """Test Measurement Description descriptor functionality."""

    def test_parse_measurement_description(self) -> None:
        """Test parsing measurement description."""
        md = MeasurementDescriptionDescriptor()
        # Description: "Temperature"
        data = b"Temperature"

        result = md.parse_value(data)
        assert result.parse_success is True
        assert isinstance(result.value, MeasurementDescriptionData)
        assert result.value.description == "Temperature"

    def test_parse_invalid_utf8(self) -> None:
        """Test parsing measurement description with invalid UTF-8."""
        md = MeasurementDescriptionDescriptor()
        data = b"\xff\xfe\xfd"  # Invalid UTF-8

        result = md.parse_value(data)
        assert result.parse_success is False
        assert "Invalid UTF-8 data" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Measurement Description has correct UUID."""
        md = MeasurementDescriptionDescriptor()
        assert str(md.uuid) == "00002912-0000-1000-8000-00805F9B34FB"
