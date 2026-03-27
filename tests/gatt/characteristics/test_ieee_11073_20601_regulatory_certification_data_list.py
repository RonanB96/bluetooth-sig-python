"""Tests for IEEE 11073-20601 Regulatory Certification Data List."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ieee_11073_20601_regulatory_certification_data_list import (
    IEEE11073RegulatoryData,
    IEEE1107320601RegulatoryCharacteristic,
)


@pytest.fixture
def characteristic() -> IEEE1107320601RegulatoryCharacteristic:
    """Create an IEEE1107320601RegulatoryCharacteristic instance."""
    return IEEE1107320601RegulatoryCharacteristic()


class TestIEEE11073Decode:
    """Tests for IEEE 11073-20601 regulatory data decoding."""

    def test_single_byte(self, characteristic: IEEE1107320601RegulatoryCharacteristic) -> None:
        """Test decoding a single byte of certification data."""
        data = bytearray(b"\x42")
        result = characteristic.parse_value(data)
        assert isinstance(result, IEEE11073RegulatoryData)
        assert result.certification_data == b"\x42"

    def test_multi_byte(self, characteristic: IEEE1107320601RegulatoryCharacteristic) -> None:
        """Test decoding multi-byte certification data."""
        raw = bytearray(b"\x01\x02\x03\x04\x05\x06\x07\x08")
        result = characteristic.parse_value(raw)
        assert result.certification_data == b"\x01\x02\x03\x04\x05\x06\x07\x08"

    def test_preserves_all_bytes(self, characteristic: IEEE1107320601RegulatoryCharacteristic) -> None:
        """Test that all bytes are preserved including embedded nulls."""
        raw = bytearray(b"\x00\xff\x00\xff\x00")
        result = characteristic.parse_value(raw)
        assert result.certification_data == b"\x00\xff\x00\xff\x00"


class TestIEEE11073Encode:
    """Tests for IEEE 11073-20601 regulatory data encoding."""

    def test_encode_single_byte(self, characteristic: IEEE1107320601RegulatoryCharacteristic) -> None:
        """Test encoding a single byte."""
        data = IEEE11073RegulatoryData(certification_data=b"\x42")
        result = characteristic.build_value(data)
        assert result == bytearray(b"\x42")

    def test_encode_multi_byte(self, characteristic: IEEE1107320601RegulatoryCharacteristic) -> None:
        """Test encoding multi-byte data."""
        data = IEEE11073RegulatoryData(certification_data=b"\x01\x02\x03\x04")
        result = characteristic.build_value(data)
        assert result == bytearray(b"\x01\x02\x03\x04")


class TestIEEE11073RoundTrip:
    """Round-trip tests for IEEE 11073-20601 regulatory data."""

    @pytest.mark.parametrize(
        "cert_data",
        [
            b"\x01",
            b"\x00\xff\x00\xff",
            b"\xde\xad\xbe\xef\xca\xfe\xba\xbe",
            bytes(range(256)),
        ],
    )
    def test_round_trip(
        self,
        characteristic: IEEE1107320601RegulatoryCharacteristic,
        cert_data: bytes,
    ) -> None:
        """Test encode -> decode round-trip."""
        original = IEEE11073RegulatoryData(certification_data=cert_data)
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
