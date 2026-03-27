"""Tests for Parent Group Object ID characteristic (0x2B9F)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.parent_group_object_id import (
    ParentGroupObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestParentGroupObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Parent Group Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> ParentGroupObjectIdCharacteristic:
        return ParentGroupObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B9F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD2, 0x04, 0x00, 0x00, 0x00, 0x00]),
                expected_value=1234,
                description="Object ID = 1234 (0x04D2 little-endian)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ParentGroupObjectIdCharacteristic()
        original = 9876543
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
