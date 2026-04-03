"""Tests for GeneralActivityInstantaneousDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.general_activity_instantaneous_data import (
    GeneralActivityInstantaneousData,
    GeneralActivityInstantaneousDataCharacteristic,
    GeneralActivityInstFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestGeneralActivityInstantaneousDataCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> GeneralActivityInstantaneousDataCharacteristic:
        return GeneralActivityInstantaneousDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B3C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xC0,  # header: first+last segment
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
                expected_value=GeneralActivityInstantaneousData(
                    header=0xC0,
                    flags=GeneralActivityInstFlags(0),
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
                        0x09,
                        0x00,
                        0x00,  # flags: bits 0+3 (EE_PER_HOUR + FAT_BURNED_PER_HOUR)
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
                expected_value=GeneralActivityInstantaneousData(
                    header=0xC0,
                    flags=(
                        GeneralActivityInstFlags.NORMAL_WALKING_EE_PER_HOUR_PRESENT
                        | GeneralActivityInstFlags.FAT_BURNED_PER_HOUR_PRESENT
                    ),
                    session_id=0,
                    sub_session_id=0,
                    relative_timestamp=0,
                    sequence_number=0,
                ),
                description="Flags with EE per hour and fat burned per hour present",
            ),
        ]
