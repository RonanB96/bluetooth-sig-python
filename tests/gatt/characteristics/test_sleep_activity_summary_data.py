"""Tests for SleepActivitySummaryDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.sleep_activity_summary_data import (
    SleepActivitySummaryData,
    SleepActivitySummaryDataCharacteristic,
    SleepActivitySummaryFlags,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSleepActivitySummaryDataCharacteristic(CommonCharacteristicTests):
    """Test suite for SleepActivitySummaryDataCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SleepActivitySummaryDataCharacteristic:
        return SleepActivitySummaryDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B42"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=SleepActivitySummaryData(
                    flags=SleepActivitySummaryFlags.TOTAL_SLEEP_TIME_PRESENT,
                    additional_data=b"",
                ),
                description="Total sleep time present flag",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00, 0x00, 0xAA, 0xBB]),
                expected_value=SleepActivitySummaryData(
                    flags=(
                        SleepActivitySummaryFlags.TOTAL_SLEEP_TIME_PRESENT
                        | SleepActivitySummaryFlags.TOTAL_WAKE_TIME_PRESENT
                    ),
                    additional_data=b"\xaa\xbb",
                ),
                description="Sleep + wake time flags with additional data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=SleepActivitySummaryData(
                    flags=SleepActivitySummaryFlags(0),
                    additional_data=b"",
                ),
                description="No flags set",
            ),
        ]
