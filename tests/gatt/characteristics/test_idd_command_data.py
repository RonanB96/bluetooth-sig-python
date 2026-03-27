"""Tests for IDDCommandDataCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_command_control_point import IDDCommandOpCode
from bluetooth_sig.gatt.characteristics.idd_command_data import (
    IDDCommandDataCharacteristic,
    IDDCommandDataPayload,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDCommandDataCharacteristic(CommonCharacteristicTests):
    """Tests for IDDCommandDataCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDCommandDataCharacteristic:
        return IDDCommandDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B26"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # opcode=RESPONSE_CODE (0x0F00 LE = [0x00, 0x0F]), no command data
                input_data=bytearray([0x00, 0x0F]),
                expected_value=IDDCommandDataPayload(
                    opcode=IDDCommandOpCode.RESPONSE_CODE,
                    command_data=b"",
                ),
                description="Response code opcode, no command data",
            ),
            CharacteristicTestData(
                # opcode=SET_BOLUS (0x0400 LE = [0x00, 0x04]), command_data=some payload
                input_data=bytearray([0x00, 0x04, 0x10, 0x20, 0x30]),
                expected_value=IDDCommandDataPayload(
                    opcode=IDDCommandOpCode.SET_BOLUS,
                    command_data=b"\x10\x20\x30",
                ),
                description="Set bolus with command data payload",
            ),
        ]
