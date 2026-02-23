"""Tests for Object Type characteristic (0x2ABF)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ObjectTypeCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectTypeCharacteristic(CommonCharacteristicTests):
    """Test suite for Object Type characteristic."""

    @pytest.fixture
    def characteristic(self) -> ObjectTypeCharacteristic:
        return ObjectTypeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ABF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xC3, 0x2A]),
                expected_value="2AC3",
                description="16-bit UUID 0x2AC3 (Object ID)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xBE, 0x2A]),
                expected_value="2ABE",
                description="16-bit UUID 0x2ABE (Object Name)",
            ),
        ]

    def test_encode_round_trip_16bit(self) -> None:
        """Verify 16-bit UUID encode/decode round-trip."""
        char = ObjectTypeCharacteristic()
        original = "2AC3"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_128bit_uuid_round_trip(self) -> None:
        """Verify 128-bit UUID encode/decode round-trip."""
        char = ObjectTypeCharacteristic()
        original = "12345678-1234-5678-9ABC-DEF012345678"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
