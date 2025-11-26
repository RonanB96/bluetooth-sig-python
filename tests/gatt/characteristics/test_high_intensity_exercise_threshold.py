"""Tests for High Intensity Exercise Threshold characteristic - demonstrating minimal test pattern."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HighIntensityExerciseThresholdCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHighIntensityExerciseThresholdCharacteristic(CommonCharacteristicTests):
    """Test suite for High Intensity Exercise Threshold characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds high intensity exercise threshold-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> HighIntensityExerciseThresholdCharacteristic:
        """Return a High Intensity Exercise Threshold characteristic instance."""
        return HighIntensityExerciseThresholdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for High Intensity Exercise Threshold characteristic."""
        return "2B4D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for high intensity exercise threshold."""
        return [
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0, description="0% threshold"),
            CharacteristicTestData(input_data=bytearray([50]), expected_value=50, description="50% threshold"),
            CharacteristicTestData(input_data=bytearray([100]), expected_value=100, description="100% threshold"),
        ]

    # === High Intensity Exercise Threshold-Specific Tests ===

    @pytest.mark.parametrize(
        "threshold_value",
        [
            0,  # 0%
            25,  # 25%
            50,  # 50%
            75,  # 75%
            100,  # 100%
        ],
    )
    def test_high_intensity_exercise_threshold_values(
        self, characteristic: HighIntensityExerciseThresholdCharacteristic, threshold_value: int
    ) -> None:
        """Test high intensity exercise threshold with various valid values."""
        data = bytearray([threshold_value])
        result = characteristic.decode_value(data)
        assert result == threshold_value

    def test_high_intensity_exercise_threshold_boundary_values(
        self, characteristic: HighIntensityExerciseThresholdCharacteristic
    ) -> None:
        """Test high intensity exercise threshold boundary values."""
        # Test minimum value (0%)
        result = characteristic.decode_value(bytearray([0]))
        assert result == 0

        # Test maximum value (255%)
        result = characteristic.decode_value(bytearray([255]))
        assert result == 255
