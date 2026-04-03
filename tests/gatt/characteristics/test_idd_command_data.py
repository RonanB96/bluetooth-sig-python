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
                input_data=bytearray([0x55, 0x0F]),
                expected_value=IDDCommandDataPayload(
                    opcode=IDDCommandOpCode.RESPONSE_CODE,
                    command_data=b"",
                ),
                description="Response code only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x5A, 0x0F, 0x01, 0x02]),
                expected_value=IDDCommandDataPayload(
                    opcode=IDDCommandOpCode.SET_THERAPY_CONTROL_STATE,
                    command_data=b"\x01\x02",
                ),
                description="Command data with payload",
            ),
        ]
