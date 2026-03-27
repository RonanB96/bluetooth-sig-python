"""Tests for ReportMapCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.report_map import ReportMapCharacteristic, ReportMapData


class TestReportMapCharacteristic:
    """Test suite for ReportMapCharacteristic.

    ReportMap has expected_type=bytes but _decode_value returns ReportMapData.
    This is a known bug, so we test _decode_value directly rather than via
    CommonCharacteristicTests (which relies on parse_value).
    """

    @pytest.fixture
    def characteristic(self) -> ReportMapCharacteristic:
        return ReportMapCharacteristic()

    def test_uuid(self, characteristic: ReportMapCharacteristic) -> None:
        """Test that the UUID matches the expected value."""
        assert characteristic.uuid == "2A4B"

    def test_decode_single_byte(self, characteristic: ReportMapCharacteristic) -> None:
        """Test decoding a single byte of report map data."""
        data = bytearray([0x05])
        result = characteristic._decode_value(data)
        assert result == ReportMapData(data=b"\x05")

    def test_decode_multi_byte(self, characteristic: ReportMapCharacteristic) -> None:
        """Test decoding multiple bytes of report map data."""
        data = bytearray([0x05, 0x01, 0x09, 0x06, 0xA1, 0x01])
        result = characteristic._decode_value(data)
        assert result == ReportMapData(data=b"\x05\x01\x09\x06\xa1\x01")

    def test_decode_all_zeros(self, characteristic: ReportMapCharacteristic) -> None:
        """Test decoding all-zero bytes."""
        data = bytearray([0x00, 0x00, 0x00])
        result = characteristic._decode_value(data)
        assert result == ReportMapData(data=b"\x00\x00\x00")

    def test_encode_decode_roundtrip(self, characteristic: ReportMapCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = ReportMapData(data=b"\x05\x01\x09\x06\xa1\x01")
        encoded = characteristic._encode_value(original)
        decoded = characteristic._decode_value(encoded)
        assert decoded == original

    def test_encode_single_byte(self, characteristic: ReportMapCharacteristic) -> None:
        """Test encoding a single byte."""
        data = ReportMapData(data=b"\xab")
        encoded = characteristic._encode_value(data)
        assert encoded == bytearray([0xAB])

    def test_encode_preserves_bytes(self, characteristic: ReportMapCharacteristic) -> None:
        """Test that encoding preserves all bytes exactly."""
        raw = bytes(range(256))
        data = ReportMapData(data=raw)
        encoded = characteristic._encode_value(data)
        assert encoded == bytearray(raw)
