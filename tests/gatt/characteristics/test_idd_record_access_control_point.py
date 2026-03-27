"""Tests for IDDRecordAccessControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.idd_record_access_control_point import (
    IDDRACPOpCode,
    IDDRACPOperator,
    IDDRecordAccessControlPointCharacteristic,
    IDDRecordAccessControlPointData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestIDDRecordAccessControlPointCharacteristic(CommonCharacteristicTests):
    """Tests for IDDRecordAccessControlPointCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> IDDRecordAccessControlPointCharacteristic:
        return IDDRecordAccessControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B27"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                # opcode=REPORT_STORED_RECORDS (0x01), operator=ALL_RECORDS (0x01)
                input_data=bytearray([0x01, 0x01]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.REPORT_STORED_RECORDS,
                    operator=IDDRACPOperator.ALL_RECORDS,
                    operand=b"",
                ),
                description="Report all stored records",
            ),
            CharacteristicTestData(
                # opcode=DELETE_STORED_RECORDS (0x02), operator=LESS_THAN_OR_EQUAL_TO (0x02),
                # operand filter value
                input_data=bytearray([0x02, 0x02, 0x0A, 0x00]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.DELETE_STORED_RECORDS,
                    operator=IDDRACPOperator.LESS_THAN_OR_EQUAL_TO,
                    operand=b"\x0a\x00",
                ),
                description="Delete records less than or equal to filter",
            ),
            CharacteristicTestData(
                # opcode=ABORT_OPERATION (0x03), operator=NULL (0x00)
                input_data=bytearray([0x03, 0x00]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.ABORT_OPERATION,
                    operator=IDDRACPOperator.NULL,
                    operand=b"",
                ),
                description="Abort operation with null operator",
            ),
        ]
