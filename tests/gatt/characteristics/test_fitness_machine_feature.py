"""Tests for Fitness Machine Feature characteristic (0x2ACC)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.fitness_machine_feature import (
    FitnessMachineFeatureCharacteristic,
    FitnessMachineFeatureData,
    FitnessMachineFeatures,
    TargetSettingFeatures,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFitnessMachineFeatureCharacteristic(CommonCharacteristicTests):
    """Test suite for Fitness Machine Feature characteristic."""

    @pytest.fixture
    def characteristic(self) -> FitnessMachineFeatureCharacteristic:
        return FitnessMachineFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ACC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=FitnessMachineFeatureData(
                    fitness_machine_features=FitnessMachineFeatures(0),
                    target_setting_features=TargetSettingFeatures(0),
                ),
                description="No features supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00]),
                expected_value=FitnessMachineFeatureData(
                    fitness_machine_features=(
                        FitnessMachineFeatures.AVERAGE_SPEED_SUPPORTED
                        | FitnessMachineFeatures.CADENCE_SUPPORTED
                        | FitnessMachineFeatures.TOTAL_DISTANCE_SUPPORTED
                    ),
                    target_setting_features=(
                        TargetSettingFeatures.SPEED_TARGET_SETTING_SUPPORTED
                        | TargetSettingFeatures.INCLINATION_TARGET_SETTING_SUPPORTED
                    ),
                ),
                description="Speed/cadence/distance with speed/inclination targets",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x74, 0x00, 0x00, 0x1F, 0x20, 0x00, 0x00]),
                expected_value=FitnessMachineFeatureData(
                    fitness_machine_features=(
                        FitnessMachineFeatures.RESISTANCE_LEVEL_SUPPORTED
                        | FitnessMachineFeatures.HEART_RATE_MEASUREMENT_SUPPORTED
                        | FitnessMachineFeatures.ELAPSED_TIME_SUPPORTED
                        | FitnessMachineFeatures.REMAINING_TIME_SUPPORTED
                        | FitnessMachineFeatures.POWER_MEASUREMENT_SUPPORTED
                    ),
                    target_setting_features=(
                        TargetSettingFeatures.SPEED_TARGET_SETTING_SUPPORTED
                        | TargetSettingFeatures.INCLINATION_TARGET_SETTING_SUPPORTED
                        | TargetSettingFeatures.RESISTANCE_TARGET_SETTING_SUPPORTED
                        | TargetSettingFeatures.POWER_TARGET_SETTING_SUPPORTED
                        | TargetSettingFeatures.HEART_RATE_TARGET_SETTING_SUPPORTED
                        | TargetSettingFeatures.INDOOR_BIKE_SIMULATION_PARAMETERS_SUPPORTED
                    ),
                ),
                description="Bike trainer with resistance/power/HR and simulation",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = FitnessMachineFeatureCharacteristic()
        original = FitnessMachineFeatureData(
            fitness_machine_features=(
                FitnessMachineFeatures.CADENCE_SUPPORTED | FitnessMachineFeatures.POWER_MEASUREMENT_SUPPORTED
            ),
            target_setting_features=TargetSettingFeatures.POWER_TARGET_SETTING_SUPPORTED,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
