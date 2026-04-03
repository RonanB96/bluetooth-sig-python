"""Tests for IDDStatusReaderControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_status_reader_control_point import (
    IDDStatusReaderControlPointCharacteristic,
    IDDStatusReaderControlPointData,
    IDDStatusReaderOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDStatusReaderControlPointCharacteristic(CommonCharacteristicTests):
    """Tests for IDDStatusReaderControlPointCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDStatusReaderControlPointCharacteristic:
        return IDDStatusReaderControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B24"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x0C, 0x03]),
                expected_value=IDDStatusReaderControlPointData(
                    opcode=IDDStatusReaderOpCode.RESET_STATUS,
                    parameter=b"",
                ),
                description="Reset status opcode",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x03, 0x0F]),
                expected_value=IDDStatusReaderControlPointData(
                    opcode=IDDStatusReaderOpCode.RESPONSE_CODE,
                    parameter=b"\x0f",
                ),
                description="Response code with success",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x30, 0x03]),
                expected_value=IDDStatusReaderControlPointData(
                    opcode=IDDStatusReaderOpCode.GET_ACTIVE_BOLUS_IDS,
                    parameter=b"",
                ),
                description="Get active bolus IDs",
            ),
        ]
