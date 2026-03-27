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
                # opcode=READ_ACTIVE_BASAL_RATE (0x01), no parameter
                input_data=bytearray([0x01]),
                expected_value=IDDStatusReaderControlPointData(
                    opcode=IDDStatusReaderOpCode.READ_ACTIVE_BASAL_RATE,
                    parameter=b"",
                ),
                description="Read active basal rate, no parameter",
            ),
            CharacteristicTestData(
                # opcode=READ_TOTAL_DAILY_INSULIN_STATUS (0x05), parameter bytes
                input_data=bytearray([0x05, 0xFF, 0x01]),
                expected_value=IDDStatusReaderControlPointData(
                    opcode=IDDStatusReaderOpCode.READ_TOTAL_DAILY_INSULIN_STATUS,
                    parameter=b"\xff\x01",
                ),
                description="Read total daily insulin status with parameter",
            ),
            CharacteristicTestData(
                # opcode=RESPONSE_CODE (0x10), parameter=success + echoed opcode
                input_data=bytearray([0x10, 0x01, 0x01]),
                expected_value=IDDStatusReaderControlPointData(
                    opcode=IDDStatusReaderOpCode.RESPONSE_CODE,
                    parameter=b"\x01\x01",
                ),
                description="Response code with success and echoed opcode",
            ),
        ]
