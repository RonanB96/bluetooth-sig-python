"""Tests for DeviceTimeControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.device_time_control_point import (
    DeviceTimeControlPointCharacteristic,
    DeviceTimeControlPointData,
    DeviceTimeControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDeviceTimeControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> DeviceTimeControlPointCharacteristic:
        return DeviceTimeControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B91"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=DeviceTimeControlPointData(
                    op_code=DeviceTimeControlPointOpCode.PROPOSE_TIME_UPDATE,
                    parameter=None,
                ),
                description="Propose Time Update opcode, no parameter bytes",
            ),
            CharacteristicTestData(
                # DTCP Response opcode (0x09), parameter = request_opcode(0x02) +
                # response_value(0x01=Success)
                input_data=bytearray([0x09, 0x02, 0x01]),
                expected_value=DeviceTimeControlPointData(
                    op_code=DeviceTimeControlPointOpCode.DTCP_RESPONSE,
                    parameter=b"\x02\x01",
                ),
                description="DTCP Response: Propose Time Update succeeded",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0xAA, 0xBB, 0xCC, 0xDD]),
                expected_value=DeviceTimeControlPointData(
                    op_code=DeviceTimeControlPointOpCode.FORCE_TIME_UPDATE,
                    parameter=b"\xaa\xbb\xcc\xdd",
                ),
                description="Force Time Update with Time Update operand bytes",
            ),
        ]
