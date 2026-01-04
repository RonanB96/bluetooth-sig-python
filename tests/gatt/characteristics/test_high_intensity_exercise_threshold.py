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
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        return [
            CharacteristicTestData(
                input_data=bytearray([0]),
                expected_value=HighIntensityExerciseThresholdData(
                    field_selector=0,
                    threshold_energy_expenditure=None,
                    threshold_metabolic_equivalent=None,
                    threshold_percentage_max_heart_rate=None,
                ),
                description="0% threshold",
            ),
            CharacteristicTestData(
                input_data=bytearray([50]),
                expected_value=HighIntensityExerciseThresholdData(
                    field_selector=50,
                    threshold_energy_expenditure=None,
                    threshold_metabolic_equivalent=None,
                    threshold_percentage_max_heart_rate=None,
                ),
                description="50% threshold",
            ),
            CharacteristicTestData(
                input_data=bytearray([100]),
                expected_value=HighIntensityExerciseThresholdData(
                    field_selector=100,
                    threshold_energy_expenditure=None,
                    threshold_metabolic_equivalent=None,
                    threshold_percentage_max_heart_rate=None,
                ),
                description="100% threshold",
            ),
        ]

    # === High Intensity Exercise Threshold-Specific Tests ===

    def test_field_selector_only(self, characteristic: HighIntensityExerciseThresholdCharacteristic) -> None:
        """Test field selector without threshold value (1 byte)."""
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        data = bytearray([42])
        result = characteristic.parse_value(data)
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == 42
        assert result.threshold_energy_expenditure is None
        assert result.threshold_metabolic_equivalent is None
        assert result.threshold_percentage_max_heart_rate is None

    def test_field_selector_1_with_energy_expenditure(
        self, characteristic: HighIntensityExerciseThresholdCharacteristic
    ) -> None:
        """Test field_selector=1 with energy expenditure threshold (3 bytes)."""
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        # field_selector=1, energy_expenditure=5 (5*1000=5000 joules)
        data = bytearray([1, 0x05, 0x00])  # little-endian uint16: 5
        result = characteristic.parse_value(data)
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == 1
        assert result.threshold_energy_expenditure == 5000
        assert result.threshold_metabolic_equivalent is None
        assert result.threshold_percentage_max_heart_rate is None

    def test_field_selector_2_with_metabolic_equivalent(
        self, characteristic: HighIntensityExerciseThresholdCharacteristic
    ) -> None:
        """Test field_selector=2 with metabolic equivalent threshold (2 bytes)."""
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        # field_selector=2, metabolic_equivalent=15 (15*0.1=1.5 MET)
        data = bytearray([2, 15])
        result = characteristic.parse_value(data)
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == 2
        assert result.threshold_energy_expenditure is None
        assert result.threshold_metabolic_equivalent == 1.5
        assert result.threshold_percentage_max_heart_rate is None

    def test_field_selector_3_with_heart_rate_percentage(
        self, characteristic: HighIntensityExerciseThresholdCharacteristic
    ) -> None:
        """Test field_selector=3 with heart rate percentage threshold (2 bytes)."""
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        # field_selector=3, heart_rate_percentage=75
        data = bytearray([3, 75])
        result = characteristic.parse_value(data)
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == 3
        assert result.threshold_energy_expenditure is None
        assert result.threshold_metabolic_equivalent is None
        assert result.threshold_percentage_max_heart_rate == 75

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
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        data = bytearray([threshold_value])
        result = characteristic.parse_value(data)
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == threshold_value
        # When only 1 byte provided, all threshold fields should be None
        assert result.threshold_energy_expenditure is None
        assert result.threshold_metabolic_equivalent is None
        assert result.threshold_percentage_max_heart_rate is None

    def test_high_intensity_exercise_threshold_boundary_values(
        self, characteristic: HighIntensityExerciseThresholdCharacteristic
    ) -> None:
        """Test high intensity exercise threshold boundary values."""
        from bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold import (
            HighIntensityExerciseThresholdData,
        )

        # Test minimum value (0%)
        result = characteristic.parse_value(bytearray([0]))
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == 0
        assert result.threshold_energy_expenditure is None
        assert result.threshold_metabolic_equivalent is None
        assert result.threshold_percentage_max_heart_rate is None

        # Test maximum value (255%)
        result = characteristic.parse_value(bytearray([255]))
        assert isinstance(result, HighIntensityExerciseThresholdData)
        assert result.field_selector == 255
        assert result.threshold_energy_expenditure is None
        assert result.threshold_metabolic_equivalent is None
        assert result.threshold_percentage_max_heart_rate is None
