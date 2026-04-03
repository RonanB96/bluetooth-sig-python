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
                input_data=bytearray([0x03, 0x03, 0x01, 0x00, 0x00, 0x00, 0x3C, 0x00]),
                expected_value=IDDHistoryDataPayload(
                    event_type=IDDHistoryEventType.THERAPY_CONTROL_STATE_CHANGED,
                    sequence_number=1,
                    relative_offset=60,
                    event_data=b"",
                ),
                description="Therapy control state changed, seq=1, offset=60s",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xCC, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF]),
                expected_value=IDDHistoryDataPayload(
                    event_type=IDDHistoryEventType.PROFILE_TEMPLATE_ACTIVATED,
                    sequence_number=10,
                    relative_offset=0,
                    event_data=b"\xff",
                ),
                description="Profile template activated with event data",
            ),
        ]
