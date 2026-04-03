"""Tests for IDDStatusChangedCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_status_changed import (
    IDDStatusChangedCharacteristic,
    IDDStatusChangedFlags,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDStatusChangedCharacteristic(CommonCharacteristicTests):
    """Tests for IDDStatusChangedCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDStatusChangedCharacteristic:
        return IDDStatusChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B20"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # flags=0x0000 → no flags
                input_data=bytearray([0x00, 0x00]),
                expected_value=IDDStatusChangedFlags(0),
                description="No status changed flags set",
            ),
            CharacteristicTestData(
                # flags=0x0001 LE → THERAPY_CONTROL_STATE_CHANGED
                input_data=bytearray([0x01, 0x00]),
                expected_value=IDDStatusChangedFlags.THERAPY_CONTROL_STATE_CHANGED,
                description="Therapy control state changed",
            ),
            CharacteristicTestData(
                # flags=0x0085 LE → THERAPY_CONTROL_STATE_CHANGED | RESERVOIR_STATUS_CHANGED | HISTORY_EVENT_RECORDED
                input_data=bytearray([0x85, 0x00]),
                expected_value=(
                    IDDStatusChangedFlags.THERAPY_CONTROL_STATE_CHANGED
                    | IDDStatusChangedFlags.RESERVOIR_STATUS_CHANGED
                    | IDDStatusChangedFlags.HISTORY_EVENT_RECORDED
                ),
                description="Therapy, reservoir, and history event changed",
            ),
        ]
