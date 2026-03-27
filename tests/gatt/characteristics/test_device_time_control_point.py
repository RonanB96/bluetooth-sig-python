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
                input_data=bytearray([0x01]),
                expected_value=DeviceTimeControlPointData(
                    op_code=DeviceTimeControlPointOpCode.GET_DEVICE_TIME,
                    parameter=None,
                ),
                description="Get device time, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0xAA, 0xBB, 0xCC, 0xDD]),
                expected_value=DeviceTimeControlPointData(
                    op_code=DeviceTimeControlPointOpCode.SET_DEVICE_TIME,
                    parameter=b"\xaa\xbb\xcc\xdd",
                ),
                description="Set device time with parameter bytes",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=DeviceTimeControlPointData(
                    op_code=DeviceTimeControlPointOpCode.CANCEL_OPERATION,
                    parameter=None,
                ),
                description="Cancel operation, no parameter",
            ),
        ]
