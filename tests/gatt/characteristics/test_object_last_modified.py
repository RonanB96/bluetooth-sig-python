"""Tests for Object Last-Modified characteristic (0x2AC2)."""

from __future__ import annotations

from datetime import datetime

import pytest

from bluetooth_sig.gatt.characteristics import ObjectLastModifiedCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectLastModifiedCharacteristic(CommonCharacteristicTests):
    """Test suite for Object Last-Modified characteristic."""

    @pytest.fixture
    def characteristic(self) -> ObjectLastModifiedCharacteristic:
        return ObjectLastModifiedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE3, 0x07, 12, 25, 10, 30, 45]),
                expected_value=datetime(2019, 12, 25, 10, 30, 45),
                description="Christmas 2019",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x07, 6, 15, 14, 0, 0]),
                expected_value=datetime(2024, 6, 15, 14, 0, 0),
                description="Summer 2024 afternoon",
            ),
        ]

    def test_custom_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = ObjectLastModifiedCharacteristic()
        original = datetime(2025, 2, 23, 9, 15, 30)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
