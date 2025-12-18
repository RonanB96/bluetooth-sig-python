"""Tests for Manufacturer Limits descriptor functionality."""

from __future__ import annotations

from bluetooth_sig.gatt.descriptors import ManufacturerLimitsDescriptor
from bluetooth_sig.gatt.descriptors.manufacturer_limits import ManufacturerLimitsData


class TestManufacturerLimitsDescriptor:
    """Test Manufacturer Limits descriptor functionality."""

    def test_parse_manufacturer_limits(self) -> None:
        """Test parsing manufacturer limits."""
        ml = ManufacturerLimitsDescriptor()
        # Lower limit: 0x0000, Upper limit: 0xFFFF
        data = b"\x00\x00\xff\xff"

        result = ml.parse_value(data)
        assert result.parse_success
        assert isinstance(result.value, ManufacturerLimitsData)
        assert result.value.min_limit == 0x0000
        assert result.value.max_limit == 0xFFFF

    def test_parse_invalid_length(self) -> None:
        """Test parsing manufacturer limits with invalid length."""
        ml = ManufacturerLimitsDescriptor()
        data = b"\x00\x00"  # Too short

        result = ml.parse_value(data)
        assert not result.parse_success
        assert "Manufacturer Limits data expected 4 bytes" in result.error_message

    def test_uuid_resolution(self) -> None:
        """Test that Manufacturer Limits has correct UUID."""
        ml = ManufacturerLimitsDescriptor()
        assert str(ml.uuid) == "00002913-0000-1000-8000-00805F9B34FB"
