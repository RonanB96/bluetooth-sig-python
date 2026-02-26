"""Tests for Temperature Statistics characteristic (0x2B11)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    TemperatureStatisticsCharacteristic,
)
from bluetooth_sig.gatt.characteristics.temperature_statistics import (
    TemperatureStatisticsData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperatureStatisticsCharacteristic(CommonCharacteristicTests):
    """Test suite for Temperature Statistics characteristic."""

    @pytest.fixture
    def characteristic(self) -> TemperatureStatisticsCharacteristic:
        return TemperatureStatisticsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B11"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=TemperatureStatisticsData(
                    average=0.0,
                    standard_deviation=0.0,
                    minimum=0.0,
                    maximum=0.0,
                    sensing_duration=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xCA,
                        0x08,  # avg: 2250 -> 22.50 C
                        0x96,
                        0x00,  # std: 150 -> 1.50 C
                        0x08,
                        0x07,  # min: 1800 -> 18.00 C
                        0x8C,
                        0x0A,  # max: 2700 -> 27.00 C
                        0x40,  # duration: raw 64 -> 1.0 s
                    ]
                ),
                expected_value=TemperatureStatisticsData(
                    average=22.5,
                    standard_deviation=1.5,
                    minimum=18.0,
                    maximum=27.0,
                    sensing_duration=1.0,
                ),
                description="Typical temperature stats",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = TemperatureStatisticsCharacteristic()
        original = TemperatureStatisticsData(
            average=22.5,
            standard_deviation=1.5,
            minimum=18.0,
            maximum=27.0,
            sensing_duration=0.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_negative_duration(self) -> None:
        """Negative sensing duration is invalid."""
        with pytest.raises(ValueError, match="cannot be negative"):
            TemperatureStatisticsData(
                average=0.0,
                standard_deviation=0.0,
                minimum=0.0,
                maximum=0.0,
                sensing_duration=-1.0,
            )
