"""Tests for ESLControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_control_point import (
    ESLControlPointCharacteristic,
    ESLCPData,
    ESLCPOpcode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestESLControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ESLControlPointCharacteristic:
        return ESLControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BFE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=ESLCPData(
                    opcode=ESLCPOpcode.PING,
                    parameters=b"",
                ),
                description="Ping command, no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x01, 0x02]),
                expected_value=ESLCPData(
                    opcode=ESLCPOpcode.READ_SENSOR_DATA,
                    parameters=b"\x01\x02",
                ),
                description="Read sensor data with parameter bytes",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=ESLCPData(
                    opcode=ESLCPOpcode.FACTORY_RESET,
                    parameters=b"",
                ),
                description="Factory reset, no parameters",
            ),
        ]
