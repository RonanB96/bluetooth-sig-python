"""Tests for IDDCommandControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_command_control_point import (
    IDDCommandControlPointCharacteristic,
    IDDCommandControlPointData,
    IDDCommandOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDCommandControlPointCharacteristic(CommonCharacteristicTests):
    """Tests for IDDCommandControlPointCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDCommandControlPointCharacteristic:
        return IDDCommandControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B25"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # opcode=SNOOZE_ANNUNCIATION (0x0100 LE = [0x00, 0x01]), no operand
                input_data=bytearray([0x00, 0x01]),
                expected_value=IDDCommandControlPointData(
                    opcode=IDDCommandOpCode.SNOOZE_ANNUNCIATION,
                    operand=b"",
                ),
                description="Snooze annunciation, no operand",
            ),
            CharacteristicTestData(
                # opcode=CONFIRM_ANNUNCIATION (0x0101 LE = [0x01, 0x01]), operand=0xABCD
                input_data=bytearray([0x01, 0x01, 0xAB, 0xCD]),
                expected_value=IDDCommandControlPointData(
                    opcode=IDDCommandOpCode.CONFIRM_ANNUNCIATION,
                    operand=b"\xab\xcd",
                ),
                description="Confirm annunciation with operand",
            ),
            CharacteristicTestData(
                # opcode=CANCEL_BOLUS (0x0401 LE = [0x01, 0x04])
                input_data=bytearray([0x01, 0x04, 0x01]),
                expected_value=IDDCommandControlPointData(
                    opcode=IDDCommandOpCode.CANCEL_BOLUS,
                    operand=b"\x01",
                ),
                description="Cancel bolus with operand byte",
            ),
        ]
