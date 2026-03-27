"""Tests for IDDHistoryDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_history_data import (
    IDDHistoryDataCharacteristic,
    IDDHistoryDataPayload,
    IDDHistoryEventType,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDHistoryDataCharacteristic(CommonCharacteristicTests):
    """Tests for IDDHistoryDataCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDHistoryDataCharacteristic:
        return IDDHistoryDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B28"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # sequence_number=1 (0x0001 LE), event_type=BOLUS_PROGRAMMED (0x02), no event data
                input_data=bytearray([0x01, 0x00, 0x02]),
                expected_value=IDDHistoryDataPayload(
                    sequence_number=1,
                    event_type=IDDHistoryEventType.BOLUS_PROGRAMMED,
                    event_data=b"",
                ),
                description="Bolus programmed event, no event data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x0A, 0x03]),
                expected_value=IDDHistoryDataPayload(
                    sequence_number=1000,
                    event_type=IDDHistoryEventType.THERAPY_CONTROL_STATE_CHANGED,
                    event_data=b"\x03",
                ),
                description="Therapy control state changed with event data",
            ),
            CharacteristicTestData(
                # sequence_number=0 (0x0000 LE), event_type=REFERENCE_TIME_BASE_CHANGED (0x01)
                input_data=bytearray([0x00, 0x00, 0x01]),
                expected_value=IDDHistoryDataPayload(
                    sequence_number=0,
                    event_type=IDDHistoryEventType.REFERENCE_TIME_BASE_CHANGED,
                    event_data=b"",
                ),
                description="Reference time base changed, sequence 0",
            ),
        ]
