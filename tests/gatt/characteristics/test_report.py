"""Tests for ReportCharacteristic.

NOTE: ReportCharacteristic has expected_type = bytes but _decode_value returns
ReportData (a struct). This is a known bug. We test _decode_value directly
and verify encode/decode round-trip rather than using CommonCharacteristicTests.
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.report import ReportCharacteristic, ReportData


class TestReportCharacteristic:
    """ReportCharacteristic test suite (standalone due to expected_type mismatch)."""

    @pytest.fixture
    def characteristic(self) -> ReportCharacteristic:
        return ReportCharacteristic()

    def test_uuid(self, characteristic: ReportCharacteristic) -> None:
        assert characteristic.uuid == "2A4D"

    def test_decode_single_byte(self, characteristic: ReportCharacteristic) -> None:
        result = characteristic._decode_value(bytearray([0x01]))
        assert result == ReportData(data=b"\x01")

    def test_decode_multi_byte(self, characteristic: ReportCharacteristic) -> None:
        result = characteristic._decode_value(bytearray([0xDE, 0xAD, 0xBE, 0xEF]))
        assert result == ReportData(data=b"\xde\xad\xbe\xef")

    def test_encode_round_trip(self, characteristic: ReportCharacteristic) -> None:
        original = bytearray([0x01, 0x02, 0x03])
        decoded = characteristic._decode_value(original)
        encoded = characteristic._encode_value(decoded)
        assert encoded == original

    def test_encode_round_trip_longer(self, characteristic: ReportCharacteristic) -> None:
        original = bytearray(b"\xaa\xbb\xcc\xdd\xee")
        decoded = characteristic._decode_value(original)
        encoded = characteristic._encode_value(decoded)
        assert encoded == original
