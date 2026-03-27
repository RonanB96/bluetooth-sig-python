"""Tests for Current Group Object ID characteristic (0x2BA0)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.current_group_object_id import (
    CurrentGroupObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCurrentGroupObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Current Group Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> CurrentGroupObjectIdCharacteristic:
        return CurrentGroupObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x39, 0x30, 0x00, 0x00, 0x00, 0x00]),
                expected_value=12345,
                description="Object ID = 12345 (0x3039 little-endian)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = CurrentGroupObjectIdCharacteristic()
        original = 65535
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
