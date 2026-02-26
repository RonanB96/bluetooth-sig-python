"""Tests for Relative Runtime in a Generic Level Range characteristic (0x2B08)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeRuntimeInAGenericLevelRangeCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_runtime_in_a_generic_level_range import (
    RelativeRuntimeInAGenericLevelRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeRuntimeInAGenericLevelRangeCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Runtime in a Generic Level Range characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeRuntimeInAGenericLevelRangeCharacteristic:
        return RelativeRuntimeInAGenericLevelRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B08"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=RelativeRuntimeInAGenericLevelRangeData(
                    relative_value=0.0,
                    minimum_generic_level=0,
                    maximum_generic_level=0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x64, 0x00, 0xE8, 0x03]),
                expected_value=RelativeRuntimeInAGenericLevelRangeData(
                    relative_value=100.0,
                    minimum_generic_level=100,
                    maximum_generic_level=1000,
                ),
                description="100% at level 100-1000",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeRuntimeInAGenericLevelRangeCharacteristic()
        original = RelativeRuntimeInAGenericLevelRangeData(
            relative_value=75.0,
            minimum_generic_level=100,
            maximum_generic_level=1000,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum level must not exceed maximum."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RelativeRuntimeInAGenericLevelRangeData(
                relative_value=50.0,
                minimum_generic_level=1000,
                maximum_generic_level=100,
            )
