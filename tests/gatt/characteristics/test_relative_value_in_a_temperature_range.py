"""Tests for Relative Value in a Temperature Range characteristic (0x2B0C)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeValueInATemperatureRangeCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_value_in_a_temperature_range import (
    RelativeValueInATemperatureRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeValueInATemperatureRangeCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Value in a Temperature Range characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeValueInATemperatureRangeCharacteristic:
        return RelativeValueInATemperatureRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B0C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=RelativeValueInATemperatureRangeData(
                    relative_value=0.0,
                    minimum_temperature=0.0,
                    maximum_temperature=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0xE8, 0x03, 0xD0, 0x07]),
                expected_value=RelativeValueInATemperatureRangeData(
                    relative_value=100.0,
                    minimum_temperature=10.0,
                    maximum_temperature=20.0,
                ),
                description="100% at 10-20 C",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeValueInATemperatureRangeCharacteristic()
        original = RelativeValueInATemperatureRangeData(
            relative_value=50.0,
            minimum_temperature=15.0,
            maximum_temperature=25.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum temperature must not exceed maximum."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RelativeValueInATemperatureRangeData(
                relative_value=50.0,
                minimum_temperature=30.0,
                maximum_temperature=10.0,
            )
