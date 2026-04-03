"""Tests for Training Status characteristic (0x2AD3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.training_status import (
    TrainingStatusCharacteristic,
    TrainingStatusData,
    TrainingStatusFlags,
    TrainingStatusValue,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrainingStatusCharacteristic(CommonCharacteristicTests):
    """Test suite for Training Status characteristic."""

    @pytest.fixture
    def characteristic(self) -> TrainingStatusCharacteristic:
        return TrainingStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01]),
                expected_value=TrainingStatusData(
                    flags=TrainingStatusFlags(0),
                    training_status=TrainingStatusValue.IDLE,
                ),
                description="Idle, no string",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x04]),
                expected_value=TrainingStatusData(
                    flags=TrainingStatusFlags(0),
                    training_status=TrainingStatusValue.HIGH_INTENSITY_INTERVAL,
                ),
                description="High intensity interval, no string",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x02, 0x57, 0x61, 0x72, 0x6D]),
                expected_value=TrainingStatusData(
                    flags=TrainingStatusFlags.TRAINING_STATUS_STRING_PRESENT,
                    training_status=TrainingStatusValue.WARMING_UP,
                    training_status_string="Warm",
                ),
                description="Warming up with status string",
            ),
        ]
