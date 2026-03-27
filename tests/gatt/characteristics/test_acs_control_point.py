"""Tests for ACSControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_control_point import (
    ACSControlPointCharacteristic,
    ACSControlPointData,
    ACSControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSControlPointCharacteristic:
        return ACSControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B33"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=ACSControlPointData(
                    opcode=ACSControlPointOpCode.SET_ACTIVE_PRESET,
                    parameters=b"",
                ),
                description="SET_ACTIVE_PRESET with no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x05, 0x0A]),
                expected_value=ACSControlPointData(
                    opcode=ACSControlPointOpCode.READ_PRESET_RECORD,
                    parameters=b"\x05\x0a",
                ),
                description="READ_PRESET_RECORD with parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF]),
                expected_value=ACSControlPointData(
                    opcode=ACSControlPointOpCode.RESPONSE,
                    parameters=b"",
                ),
                description="RESPONSE opcode with no parameters",
            ),
        ]
