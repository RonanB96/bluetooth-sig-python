"""Tests for Object ID characteristic (0x2AC3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ObjectIdCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> ObjectIdCharacteristic:
        return ObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=1,
                description="Object ID = 1",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ObjectIdCharacteristic()
        original = 12345678
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
