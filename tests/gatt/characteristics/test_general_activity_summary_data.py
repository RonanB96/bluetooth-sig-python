"""Tests for GeneralActivitySummaryDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.general_activity_summary_data import (
    GeneralActivitySummaryData,
    GeneralActivitySummaryDataCharacteristic,
    GeneralActivitySummaryFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestGeneralActivitySummaryDataCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> GeneralActivitySummaryDataCharacteristic:
        return GeneralActivitySummaryDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x88, 0x13]),
                expected_value=GeneralActivitySummaryData(
                    flags=GeneralActivitySummaryFlags.STEPS_PRESENT,
                    steps=5000,
                ),
                description="Steps only, 5000 steps",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x1F,
                        0x10,
                        0x27,
                        0x40,
                        0x1F,
                        0x00,
                        0x20,
                        0x1C,
                        0x00,
                        0x3C,
                        0x5E,
                        0x01,
                    ]
                ),
                expected_value=GeneralActivitySummaryData(
                    flags=(
                        GeneralActivitySummaryFlags.STEPS_PRESENT
                        | GeneralActivitySummaryFlags.DISTANCE_PRESENT
                        | GeneralActivitySummaryFlags.DURATION_PRESENT
                        | GeneralActivitySummaryFlags.INTENSITY_PRESENT
                        | GeneralActivitySummaryFlags.CALORIES_PRESENT
                    ),
                    steps=10000,
                    distance=8000,
                    duration=7200,
                    intensity=60,
                    calories=350,
                ),
                description="All fields present",
            ),
        ]
