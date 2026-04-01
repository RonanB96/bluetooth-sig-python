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
                input_data=bytearray(
                    [
                        0xC0,  # header: first+last segment
                        0x00,  # flags: none set
                        0x01,
                        0x00,  # session_id: 1
                        0x02,
                        0x00,  # sub_session_id: 2
                        0x0A,
                        0x00,
                        0x00,
                        0x00,  # relative_timestamp: 10
                        0x01,
                        0x00,
                        0x00,
                        0x00,  # sequence_number: 1
                    ]
                ),
                expected_value=StepCounterActivitySummaryData(
                    header=0xC0,
                    flags=StepCounterActivitySummaryFlags(0),
                    session_id=1,
                    sub_session_id=2,
                    relative_timestamp=10,
                    sequence_number=1,
                ),
                description="Minimal data, no optional fields",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xC0,  # header
                        0x05,  # flags: NORMAL_WALKING_STEPS + FLOOR_STEPS (bits 0+2)
                        0x00,
                        0x00,  # session_id: 0
                        0x00,
                        0x00,  # sub_session_id: 0
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # relative_timestamp: 0
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # sequence_number: 0
                    ]
                ),
                expected_value=StepCounterActivitySummaryData(
                    header=0xC0,
                    flags=(
                        StepCounterActivitySummaryFlags.NORMAL_WALKING_STEPS_PRESENT
                        | StepCounterActivitySummaryFlags.FLOOR_STEPS_PRESENT
                    ),
                    session_id=0,
                    sub_session_id=0,
                    relative_timestamp=0,
                    sequence_number=0,
                ),
                description="Flags with walking and floor steps present",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = StepCounterActivitySummaryDataCharacteristic()
        original = StepCounterActivitySummaryData(
            header=0xC0,
            flags=StepCounterActivitySummaryFlags.NORMAL_WALKING_STEPS_PRESENT,
            session_id=5,
            sub_session_id=1,
            relative_timestamp=100,
            sequence_number=42,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
