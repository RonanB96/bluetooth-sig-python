"""Tests for BR-EDR Handover Data characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.br_edr_handover_data import (
    BREDRHandoverDataCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBREDRHandoverDataCharacteristic(CommonCharacteristicTests):
    """Test suite for BR-EDR Handover Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> BREDRHandoverDataCharacteristic:
        return BREDRHandoverDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B38"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte handover data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xDE, 0xAD, 0xBE, 0xEF, 0xCA, 0xFE]),
                expected_value=b"\xde\xad\xbe\xef\xca\xfe",
                description="Multi-byte handover data",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = BREDRHandoverDataCharacteristic()
        original = b"\x01\x02\x03\x04\x05"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
