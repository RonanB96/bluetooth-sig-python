"""Tests for Temperature 8 Statistics characteristic (0x2B0F)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    Temperature8StatisticsCharacteristic,
)
from bluetooth_sig.gatt.characteristics.temperature_8_statistics import (
    Temperature8StatisticsData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperature8StatisticsCharacteristic(CommonCharacteristicTests):
    """Test suite for Temperature 8 Statistics characteristic."""

    @pytest.fixture
    def characteristic(self) -> Temperature8StatisticsCharacteristic:
        return Temperature8StatisticsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B0F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=Temperature8StatisticsData(
                    average=0.0,
                    standard_deviation=0.0,
                    minimum=0.0,
                    maximum=0.0,
                    sensing_duration=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x14, 0x04, 0x0A, 0x1E, 0x40]),
                expected_value=Temperature8StatisticsData(
                    average=10.0,
                    standard_deviation=2.0,
                    minimum=5.0,
                    maximum=15.0,
                    sensing_duration=1.0,
                ),
                description="Typical temp stats (raw 64 = 1.1^0 = 1.0 s)",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = Temperature8StatisticsCharacteristic()
        original = Temperature8StatisticsData(
            average=10.0,
            standard_deviation=2.0,
            minimum=5.0,
            maximum=15.0,
            sensing_duration=0.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_negative_duration(self) -> None:
        """Negative sensing duration is invalid."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Temperature8StatisticsData(
                average=0.0,
                standard_deviation=0.0,
                minimum=0.0,
                maximum=0.0,
                sensing_duration=-1.0,
            )
