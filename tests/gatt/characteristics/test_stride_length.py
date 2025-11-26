"""Tests for Stride Length characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import StrideLengthCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestStrideLengthCharacteristic(CommonCharacteristicTests):
    """Test suite for Stride Length characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds stride length-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> StrideLengthCharacteristic:
        """Return a Stride Length characteristic instance."""
        return StrideLengthCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Stride Length characteristic."""
        return "2B49"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for stride length."""
        return [
            CharacteristicTestData(input_data=bytearray([0, 0]), expected_value=0.0, description="Zero stride length"),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]), expected_value=1.0, description="1 meter stride"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD0, 0x07]), expected_value=2.0, description="2 meter stride"
            ),
        ]

    # === Stride Length-Specific Tests ===

    @pytest.mark.parametrize(
        "raw_value,expected_length",
        [
            (0, 0.0),  # 0 mm
            (1000, 1.0),  # 1000 mm = 1 m
            (2000, 2.0),  # 2000 mm = 2 m
            (750, 0.75),  # 750 mm = 0.75 m
        ],
    )
    def test_stride_length_values(
        self, characteristic: StrideLengthCharacteristic, raw_value: int, expected_length: float
    ) -> None:
        """Test stride length with various valid values."""
        data = bytearray([raw_value & 0xFF, (raw_value >> 8) & 0xFF])
        result = characteristic.decode_value(data)
        assert result == expected_length

    def test_stride_length_boundary_values(self, characteristic: StrideLengthCharacteristic) -> None:
        """Test stride length boundary values."""
        # Test minimum value (0 m)
        result = characteristic.decode_value(bytearray([0, 0]))
        assert result == 0.0

        # Test maximum value (65.535 m)
        result = characteristic.decode_value(bytearray([0xFF, 0xFF]))
        assert result == 65.535
