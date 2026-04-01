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
                input_data=bytearray([0x33, 0x0F]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.REPORT_STORED_RECORDS,
                    operator=IDDRACPOperator.NULL,
                    operand=b"",
                ),
                description="Report stored records",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0F, 0x0F, 0x0F]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.RESPONSE_CODE,
                    operator=IDDRACPOperator.NULL,
                    operand=b"\x0f",
                ),
                description="Response code",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x3C, 0x33]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.DELETE_STORED_RECORDS,
                    operator=IDDRACPOperator.ALL_RECORDS,
                    operand=b"",
                ),
                description="Delete all stored records",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x55, 0x0F]),
                expected_value=IDDRecordAccessControlPointData(
                    opcode=IDDRACPOpCode.ABORT_OPERATION,
                    operator=IDDRACPOperator.NULL,
                    operand=b"",
                ),
                description="Abort operation",
            ),
        ]
