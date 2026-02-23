"""Tests for Relative Value in a Voltage Range characteristic (0x2B09)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import (
    RelativeValueInAVoltageRangeCharacteristic,
)
from bluetooth_sig.gatt.characteristics.relative_value_in_a_voltage_range import (
    RelativeValueInAVoltageRangeData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRelativeValueInAVoltageRangeCharacteristic(CommonCharacteristicTests):
    """Test suite for Relative Value in a Voltage Range characteristic."""

    @pytest.fixture
    def characteristic(self) -> RelativeValueInAVoltageRangeCharacteristic:
        return RelativeValueInAVoltageRangeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B09"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=RelativeValueInAVoltageRangeData(
                    relative_value=0.0,
                    minimum_voltage=0.0,
                    maximum_voltage=0.0,
                ),
                description="All zeros",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x04, 0x40, 0x06]),
                expected_value=RelativeValueInAVoltageRangeData(
                    relative_value=50.0,
                    minimum_voltage=16.0,
                    maximum_voltage=25.0,
                ),
                description="50% at 16-25 V",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RelativeValueInAVoltageRangeCharacteristic()
        original = RelativeValueInAVoltageRangeData(
            relative_value=50.0,
            minimum_voltage=3.5,
            maximum_voltage=5.0,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_validation_rejects_inverted_range(self) -> None:
        """Minimum voltage must not exceed maximum."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RelativeValueInAVoltageRangeData(
                relative_value=50.0,
                minimum_voltage=10.0,
                maximum_voltage=5.0,
            )
