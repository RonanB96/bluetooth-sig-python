"""Tests for Relative Value in a Period of Day characteristic (0x2B0B)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeValueInAPeriodOfDayCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_value_in_a_period_of_day import (
    RelativeValueInAPeriodOfDayData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeValueInAPeriodOfDayCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Value in a Period of Day characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeValueInAPeriodOfDayCharacteristic:
        return RelativeValueInAPeriodOfDayCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B0B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=RelativeValueInAPeriodOfDayData(
                    relative_value=0.0,
                    start_time=0.0,
                    end_time=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x3C, 0xB4]),
                expected_value=RelativeValueInAPeriodOfDayData(
                    relative_value=100.0,
                    start_time=6.0,
                    end_time=18.0,
                ),
                description="100% from 06:00 to 18:00",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeValueInAPeriodOfDayCharacteristic()
        original = RelativeValueInAPeriodOfDayData(
            relative_value=50.0,
            start_time=8.0,
            end_time=17.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
