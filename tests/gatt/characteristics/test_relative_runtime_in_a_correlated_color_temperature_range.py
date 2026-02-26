"""Tests for Relative Runtime in a CCT Range characteristic (0x2BE5)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_runtime_in_a_correlated_color_temperature_range import (
    RelativeRuntimeInACCTRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeRuntimeInACCTRangeCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Runtime in a CCT Range characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic:
        return RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BE5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=RelativeRuntimeInACCTRangeData(
                    relative_runtime=0.0,
                    minimum_cct=0,
                    maximum_cct=0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0xBC, 0x0A, 0x3C, 0x13]),
                expected_value=RelativeRuntimeInACCTRangeData(
                    relative_runtime=100.0,
                    minimum_cct=2748,
                    maximum_cct=4924,
                ),
                description="100% at warm-to-cool CCT",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeRuntimeInACorrelatedColorTemperatureRangeCharacteristic()
        original = RelativeRuntimeInACCTRangeData(
            relative_runtime=50.0,
            minimum_cct=2700,
            maximum_cct=6500,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum CCT must not exceed maximum."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RelativeRuntimeInACCTRangeData(
                relative_runtime=50.0,
                minimum_cct=6500,
                maximum_cct=2700,
            )
