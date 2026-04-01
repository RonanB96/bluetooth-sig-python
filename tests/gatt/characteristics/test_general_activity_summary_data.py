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
                input_data=bytearray(
                    [
                        0xC0,  # header: first+last segment
                        0x00,
                        0x00,
                        0x00,
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
                expected_value=GeneralActivitySummaryData(
                    header=0xC0,
                    flags=GeneralActivitySummaryFlags(0),
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
                        0x81,
                        0x00,
                        0x00,
                        0x00,  # flags: bits 0 + 7 (EE + distance)
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
                expected_value=GeneralActivitySummaryData(
                    header=0xC0,
                    flags=(
                        GeneralActivitySummaryFlags.NORMAL_WALKING_EE_PRESENT
                        | GeneralActivitySummaryFlags.DISTANCE_PRESENT
                    ),
                    session_id=0,
                    sub_session_id=0,
                    relative_timestamp=0,
                    sequence_number=0,
                ),
                description="Flags with EE and distance present",
            ),
        ]
