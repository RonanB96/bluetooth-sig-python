"""Tests for Relative Runtime in a Current Range characteristic (0x2B07)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeRuntimeInACurrentRangeCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_runtime_in_a_current_range import (
    RelativeRuntimeInACurrentRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeRuntimeInACurrentRangeCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Runtime in a Current Range characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeRuntimeInACurrentRangeCharacteristic:
        return RelativeRuntimeInACurrentRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B07"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=RelativeRuntimeInACurrentRangeData(
                    relative_runtime=0.0,
                    minimum_current=0.0,
                    maximum_current=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xC8, 0x32, 0x00, 0xC8, 0x00]),
                expected_value=RelativeRuntimeInACurrentRangeData(
                    relative_runtime=100.0,
                    minimum_current=0.5,
                    maximum_current=2.0,
                ),
                description="100% at 0.5-2.0 A",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeRuntimeInACurrentRangeCharacteristic()
        original = RelativeRuntimeInACurrentRangeData(
            relative_runtime=50.0,
            minimum_current=0.5,
            maximum_current=2.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum current must not exceed maximum."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RelativeRuntimeInACurrentRangeData(
                relative_runtime=50.0,
                minimum_current=5.0,
                maximum_current=1.0,
            )
