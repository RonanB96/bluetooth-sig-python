"""Tests for Relative Value in an Illuminance Range characteristic (0x2B0A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeValueInAnIlluminanceRangeCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_value_in_an_illuminance_range import (
    RelativeValueInAnIlluminanceRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeValueInAnIlluminanceRangeCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Value in an Illuminance Range characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeValueInAnIlluminanceRangeCharacteristic:
        return RelativeValueInAnIlluminanceRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B0A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=RelativeValueInAnIlluminanceRangeData(
                    relative_value=0.0,
                    minimum_illuminance=0.0,
                    maximum_illuminance=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x10, 0x27, 0x00, 0x50, 0xC3, 0x00]),
                expected_value=RelativeValueInAnIlluminanceRangeData(
                    relative_value=50.0,
                    minimum_illuminance=100.0,
                    maximum_illuminance=500.0,
                ),
                description="50% at 100-500 lux",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeValueInAnIlluminanceRangeCharacteristic()
        original = RelativeValueInAnIlluminanceRangeData(
            relative_value=75.0,
            minimum_illuminance=100.0,
            maximum_illuminance=500.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum illuminance must not exceed maximum."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RelativeValueInAnIlluminanceRangeData(
                relative_value=50.0,
                minimum_illuminance=500.0,
                maximum_illuminance=100.0,
            )
