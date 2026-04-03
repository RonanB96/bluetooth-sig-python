"""Tests for SleepActivityInstantaneousDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.sleep_activity_instantaneous_data import (
    SleepActivityInstantaneousData,
    SleepActivityInstantaneousDataCharacteristic,
    SleepActivityInstantaneousFlags,
    SleepStage,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSleepActivityInstantaneousDataCharacteristic(CommonCharacteristicTests):
    """Test suite for SleepActivityInstantaneousDataCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SleepActivityInstantaneousDataCharacteristic:
        return SleepActivityInstantaneousDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B41"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x00, 0x02, 0x00, 0x00]),
                expected_value=SleepActivityInstantaneousData(
                    flags=SleepActivityInstantaneousFlags.SLEEP_STAGE_PRESENT,
                    sleep_stage=SleepStage.SLEEP,
                    additional_data=b"",
                ),
                description="Sleep stage present, stage=SLEEP",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x80, 0x01, 0x00, 0x00]),
                expected_value=SleepActivityInstantaneousData(
                    flags=SleepActivityInstantaneousFlags.DEVICE_WORN,
                    sleep_stage=SleepStage.WAKE,
                    additional_data=b"",
                ),
                description="Device worn, stage=WAKE",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x00, 0x04, 0x00, 0x00, 0xFF]),
                expected_value=SleepActivityInstantaneousData(
                    flags=SleepActivityInstantaneousFlags.SLEEP_STAGE_PRESENT,
                    sleep_stage=SleepStage.REM,
                    additional_data=b"\xff",
                ),
                description="Sleep stage present, stage=REM, with additional data",
            ),
        ]
