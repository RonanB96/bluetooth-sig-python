"""Tests for Step Counter Activity Summary Data characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.step_counter_activity_summary_data import (
    StepCounterActivitySummaryData,
    StepCounterActivitySummaryDataCharacteristic,
    StepCounterActivitySummaryFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestStepCounterActivitySummaryDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Step Counter Activity Summary Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> StepCounterActivitySummaryDataCharacteristic:
        return StepCounterActivitySummaryDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B40"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=StepCounterActivitySummaryData(
                    flags=StepCounterActivitySummaryFlags(0),
                ),
                description="Flags only, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x07,
                        0x00,  # flags: all present
                        0xE8,
                        0x03,
                        0x00,  # step_count: 1000 (uint24 LE)
                        0xD0,
                        0x07,
                        0x00,  # distance: 2000 (uint24 LE)
                        0xF4,
                        0x01,  # calories: 500 (uint16 LE)
                    ]
                ),
                expected_value=StepCounterActivitySummaryData(
                    flags=(
                        StepCounterActivitySummaryFlags.STEP_COUNT_PRESENT
                        | StepCounterActivitySummaryFlags.DISTANCE_PRESENT
                        | StepCounterActivitySummaryFlags.CALORIES_PRESENT
                    ),
                    step_count=1000,
                    distance=2000,
                    calories=500,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,
                        0x00,  # flags: step_count only
                        0x64,
                        0x00,
                        0x00,  # step_count: 100 (uint24 LE)
                    ]
                ),
                expected_value=StepCounterActivitySummaryData(
                    flags=StepCounterActivitySummaryFlags.STEP_COUNT_PRESENT,
                    step_count=100,
                ),
                description="Step count only",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = StepCounterActivitySummaryDataCharacteristic()
        original = StepCounterActivitySummaryData(
            flags=(
                StepCounterActivitySummaryFlags.STEP_COUNT_PRESENT | StepCounterActivitySummaryFlags.CALORIES_PRESENT
            ),
            step_count=5000,
            calories=250,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
