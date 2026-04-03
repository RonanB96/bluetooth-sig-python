"""Tests for CardioRespiratory Activity Summary Data characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cardiorespiratory_activity_summary_data import (
    CardioRespiratoryActivitySummaryData,
    CardioRespiratoryActivitySummaryDataCharacteristic,
    CardioRespiratorySummaryFlags,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCardioRespiratoryActivitySummaryDataCharacteristic(CommonCharacteristicTests):
    """Test suite for CardioRespiratory Activity Summary Data."""

    @pytest.fixture
    def characteristic(self) -> CardioRespiratoryActivitySummaryDataCharacteristic:
        return CardioRespiratoryActivitySummaryDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=CardioRespiratoryActivitySummaryData(
                    flags=CardioRespiratorySummaryFlags(0x00000000),
                    additional_data=b"",
                ),
                description="No optional fields present (flags=0)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07, 0x00, 0x00, 0x00, 0xAA, 0xBB, 0xCC]),
                expected_value=CardioRespiratoryActivitySummaryData(
                    flags=CardioRespiratorySummaryFlags(0x00000007),
                    additional_data=b"\xaa\xbb\xcc",
                ),
                description="Flags 0x0007 with summary data",
            ),
        ]
