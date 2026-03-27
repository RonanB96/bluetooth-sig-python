"""Tests for ESL Address characteristic (0x2BF6)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_address import (
    ESLAddressCharacteristic,
    ESLAddressData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestESLAddressCharacteristic(CommonCharacteristicTests):
    """Test suite for ESL Address characteristic."""

    @pytest.fixture
    def characteristic(self) -> ESLAddressCharacteristic:
        return ESLAddressCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x00]),
                expected_value=ESLAddressData(esl_id=5, group_id=0),
                description="ESL_ID=5, Group_ID=0",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFE, 0x3F]),
                expected_value=ESLAddressData(esl_id=0xFE, group_id=0x3F),
                description="ESL_ID=254, Group_ID=63",
            ),
        ]

    def test_broadcast_address(self, characteristic: ESLAddressCharacteristic) -> None:
        """ESL_ID=0xFF is the broadcast address per spec §3.1.1.2."""
        result = characteristic.parse_value(bytearray([0xFF, 0x05]))
        assert result.esl_id == 0xFF
        assert result.group_id == 5

    def test_max_group_id(self, characteristic: ESLAddressCharacteristic) -> None:
        """Group_ID max is 127 (7-bit field, bits 8-14)."""
        # 0x7F << 8 = 0x7F00, ESL_ID=0x00 → raw = 0x7F00
        result = characteristic.parse_value(bytearray([0x00, 0x7F]))
        assert result.esl_id == 0
        assert result.group_id == 127

    def test_rfu_bit_ignored(self, characteristic: ESLAddressCharacteristic) -> None:
        """Bit 15 is RFU and should not affect parsed fields."""
        # raw = 0x8005 → ESL_ID=5, Group_ID=0 (bit 15 set but ignored)
        result = characteristic.parse_value(bytearray([0x05, 0x80]))
        assert result.esl_id == 5
        assert result.group_id == 0

    def test_roundtrip(self, characteristic: ESLAddressCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = ESLAddressData(esl_id=0xAB, group_id=0x55)
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
