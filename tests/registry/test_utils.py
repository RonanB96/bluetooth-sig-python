"""Tests for registry utility functions."""

from __future__ import annotations

from bluetooth_sig.registry.utils import parse_bluetooth_uuid
from bluetooth_sig.types.uuid import BluetoothUUID


class TestParseBluetoothUUID:
    """Test the parse_bluetooth_uuid utility function."""

    def test_parse_bluetooth_uuid_object(self) -> None:
        """Test that BluetoothUUID objects are returned as-is."""
        uuid = BluetoothUUID("180F")
        result = parse_bluetooth_uuid(uuid)
        assert result is uuid

    def test_parse_small_integer_with_padding(self) -> None:
        """Test that small integers are zero-padded to 4 characters."""
        # 3 (0x0003) should become "0003"
        result = parse_bluetooth_uuid(3)
        assert result.short_form == "0003"

        # 1 (0x0001) should become "0001"
        result = parse_bluetooth_uuid(1)
        assert result.short_form == "0001"

        # 15 (0x000F) should become "000F"
        result = parse_bluetooth_uuid(15)
        assert result.short_form == "000F"

    def test_parse_16bit_uuid_without_padding(self) -> None:
        """Test that 4-digit hex integers don't need padding."""
        # 0x1000 = 4096 should become "1000"
        result = parse_bluetooth_uuid(0x1000)
        assert result.short_form == "1000"

        # 0xFFFF = 65535 should become "FFFF"
        result = parse_bluetooth_uuid(0xFFFF)
        assert result.short_form == "FFFF"

    def test_parse_large_integer_no_padding(self) -> None:
        """Test that integers beyond 16-bit range raise ValueError."""
        import pytest

        # 0x12345 is 5 hex digits - invalid (not 4 or 32)
        with pytest.raises(ValueError, match="Invalid UUID length"):
            parse_bluetooth_uuid(0x12345)

        # 0x100000 is 6 hex digits - invalid
        with pytest.raises(ValueError, match="Invalid UUID length"):
            parse_bluetooth_uuid(0x100000)

    def test_parse_string_uuid(self) -> None:
        """Test parsing string UUIDs."""
        # String with 0x prefix
        result = parse_bluetooth_uuid("0x180F")
        assert result.short_form == "180F"

        # String without prefix
        result = parse_bluetooth_uuid("180F")
        assert result.short_form == "180F"

        # String with 0X prefix (uppercase X)
        result = parse_bluetooth_uuid("0X180F")
        assert result.short_form == "180F"

    def test_parse_128bit_uuid_string(self) -> None:
        """Test parsing 128-bit UUID strings."""
        uuid_str = "0000180F-0000-1000-8000-00805F9B34FB"
        result = parse_bluetooth_uuid(uuid_str)
        # BluetoothUUID normalizes by removing dashes
        assert result.normalized == "0000180F00001000800000805F9B34FB"

    def test_parse_zero(self) -> None:
        """Test parsing zero value."""
        result = parse_bluetooth_uuid(0)
        assert result.short_form == "0000"

    def test_parse_boundary_values(self) -> None:
        """Test boundary values for 16-bit UUID range."""
        import pytest

        # Maximum 16-bit value
        result = parse_bluetooth_uuid(65535)  # 0xFFFF
        assert result.short_form == "FFFF"

        # Just beyond 16-bit range - invalid (5 hex digits)
        with pytest.raises(ValueError, match="Invalid UUID length"):
            parse_bluetooth_uuid(65536)  # 0x10000

    def test_parse_protocol_uuid_examples(self) -> None:
        """Test specific protocol UUIDs mentioned in the protocol registry."""
        # L2CAP = 0x0100 = 256
        result = parse_bluetooth_uuid(256)
        assert result.short_form == "0100"

        # RFCOMM = 0x0003 = 3
        result = parse_bluetooth_uuid(3)
        assert result.short_form == "0003"

        # AVDTP = 0x0019 = 25
        result = parse_bluetooth_uuid(25)
        assert result.short_form == "0019"

        # BNEP = 0x000F = 15
        result = parse_bluetooth_uuid(15)
        assert result.short_form == "000F"
