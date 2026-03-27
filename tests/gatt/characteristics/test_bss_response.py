"""Tests for BSS Response characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bss_response import (
    BSSResponseCharacteristic,
    BSSResponseData,
    BSSResponseOpCode,
    BSSResponseResult,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBSSResponseCharacteristic(CommonCharacteristicTests):
    """Test suite for BSS Response characteristic."""

    @pytest.fixture
    def characteristic(self) -> BSSResponseCharacteristic:
        return BSSResponseCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00]),
                expected_value=BSSResponseData(
                    opcode=BSSResponseOpCode.ADD_SOURCE,
                    result=BSSResponseResult.SUCCESS,
                ),
                description="Add source success",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x02]),
                expected_value=BSSResponseData(
                    opcode=BSSResponseOpCode.REMOVE_SOURCE,
                    result=BSSResponseResult.INVALID_SOURCE_ID,
                ),
                description="Remove source invalid source ID",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = BSSResponseCharacteristic()
        original = BSSResponseData(
            opcode=BSSResponseOpCode.MODIFY_SOURCE,
            result=BSSResponseResult.OPCODE_NOT_SUPPORTED,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
