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
                input_data=bytearray([0x5A, 0x0F]),
                expected_value=IDDCommandControlPointData(
                    opcode=IDDCommandOpCode.SET_THERAPY_CONTROL_STATE,
                    operand=b"",
                ),
                description="Set therapy control state",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x55, 0x0F, 0x0F]),
                expected_value=IDDCommandControlPointData(
                    opcode=IDDCommandOpCode.RESPONSE_CODE,
                    operand=b"\x0f",
                ),
                description="Response code with success",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x0F, 0x01, 0x02]),
                expected_value=IDDCommandControlPointData(
                    opcode=IDDCommandOpCode.SET_TBR_ADJUSTMENT,
                    operand=b"\x01\x02",
                ),
                description="Set TBR adjustment with operand",
            ),
        ]
