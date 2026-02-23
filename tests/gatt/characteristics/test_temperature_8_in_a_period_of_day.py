"""Tests for Temperature 8 in a Period of Day characteristic (0x2B0E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    Temperature8InAPeriodOfDayCharacteristic,
)
from bluetooth_sig.gatt.characteristics.temperature_8_in_a_period_of_day import (
    Temperature8InAPeriodOfDayData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperature8InAPeriodOfDayCharacteristic(CommonCharacteristicTests):
    """Test suite for Temperature 8 in a Period of Day characteristic."""

    @pytest.fixture
    def characteristic(self) -> Temperature8InAPeriodOfDayCharacteristic:
        return Temperature8InAPeriodOfDayCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B0E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=Temperature8InAPeriodOfDayData(
                    temperature=0.0,
                    start_time=0.0,
                    end_time=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x2C, 0x3C, 0xB4]),
                expected_value=Temperature8InAPeriodOfDayData(
                    temperature=22.0,
                    start_time=6.0,
                    end_time=18.0,
                ),
                description="22 C from 06:00 to 18:00",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = Temperature8InAPeriodOfDayCharacteristic()
        original = Temperature8InAPeriodOfDayData(
            temperature=10.0,
            start_time=8.0,
            end_time=20.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_negative_temperature(self) -> None:
        """Verify negative temperature decodes correctly."""
        char = Temperature8InAPeriodOfDayCharacteristic()
        # sint8 -20 = 0xEC, representing -10.0 C
        result = char.parse_value(bytearray([0xEC, 0x00, 0x00]))
        assert result.temperature == -10.0
