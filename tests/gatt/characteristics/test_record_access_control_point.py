"""Tests for Record Access Control Point characteristic (0x2A52)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.record_access_control_point import (
    RACPOpCode,
    RACPOperator,
    RecordAccessControlPointCharacteristic,
    RecordAccessControlPointData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRecordAccessControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Record Access Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> RecordAccessControlPointCharacteristic:
        return RecordAccessControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A52"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x01]),
                expected_value=RecordAccessControlPointData(
                    opcode=RACPOpCode.REPORT_STORED_RECORDS,
                    operator=RACPOperator.ALL_RECORDS,
                ),
                description="Report all stored records",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00]),
                expected_value=RecordAccessControlPointData(
                    opcode=RACPOpCode.ABORT_OPERATION,
                    operator=RACPOperator.NULL,
                ),
                description="Abort operation",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06, 0x00, 0x01, 0x01]),
                expected_value=RecordAccessControlPointData(
                    opcode=RACPOpCode.RESPONSE_CODE,
                    operator=RACPOperator.NULL,
                    operand=b"\x01\x01",
                ),
                description="Response code: success for Report Stored Records",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RecordAccessControlPointCharacteristic()
        original = RecordAccessControlPointData(
            opcode=RACPOpCode.DELETE_STORED_RECORDS,
            operator=RACPOperator.LAST_RECORD,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
