"""Tests for Object First-Created characteristic (0x2AC1)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics import ObjectFirstCreatedCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectFirstCreatedCharacteristic(CommonCharacteristicTests):
    """Test suite for Object First-Created characteristic."""

    @pytest.fixture
    def characteristic(self) -> ObjectFirstCreatedCharacteristic:
        return ObjectFirstCreatedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE3, 0x07, 12, 25, 10, 30, 45]),
                expected_value=datetime(2019, 12, 25, 10, 30, 45),
                description="Christmas 2019",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE4, 0x07, 1, 1, 0, 0, 0]),
                expected_value=datetime(2020, 1, 1, 0, 0, 0),
                description="New Year 2020 midnight",
            ),
        ]

    def test_custom_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ObjectFirstCreatedCharacteristic()
        original = datetime(2025, 6, 15, 14, 30, 0)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
