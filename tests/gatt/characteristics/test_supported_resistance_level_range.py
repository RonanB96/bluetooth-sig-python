"""Tests for SupportedResistanceLevelRangeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import SupportedResistanceLevelRangeCharacteristic
from bluetooth_sig.gatt.characteristics.supported_resistance_level_range import (
    SupportedResistanceLevelRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSupportedResistanceLevelRangeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> SupportedResistanceLevelRangeCharacteristic:
        return SupportedResistanceLevelRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD6"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=SupportedResistanceLevelRangeData(
                    minimum=0.0,
                    maximum=0.0,
                    minimum_increment=0.0,
                ),
                description="Zero resistance range",
            ),
            CharacteristicTestData(
                # min=10 (raw 1), max=200 (raw 20), inc=10 (raw 1)
                input_data=bytearray([0x01, 0x14, 0x01]),
                expected_value=SupportedResistanceLevelRangeData(
                    minimum=10.0,
                    maximum=200.0,
                    minimum_increment=10.0,
                ),
                description="Typical bike resistance range (10-200, step 10)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF]),
                expected_value=SupportedResistanceLevelRangeData(
                    minimum=2550.0,
                    maximum=2550.0,
                    minimum_increment=2550.0,
                ),
                description="Maximum resistance range",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = SupportedResistanceLevelRangeCharacteristic()
        original = SupportedResistanceLevelRangeData(
            minimum=20.0,
            maximum=500.0,
            minimum_increment=10.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum > maximum is invalid."""
        with pytest.raises(ValueError, match="cannot be greater"):
            SupportedResistanceLevelRangeData(minimum=200.0, maximum=50.0, minimum_increment=10.0)

    def test_validation_rejects_negative(self) -> None:
        """Negative resistance is invalid for uint8."""
        with pytest.raises(ValueError, match="outside valid range"):
            SupportedResistanceLevelRangeData(minimum=-10.0, maximum=100.0, minimum_increment=10.0)
