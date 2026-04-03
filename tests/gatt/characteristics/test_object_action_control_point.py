"""Tests for ObjectActionControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.object_action_control_point import (
    OACPData,
    OACPOpcode,
    ObjectActionControlPointCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectActionControlPointCharacteristic(CommonCharacteristicTests):
    """Test Object Action Control Point characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> ObjectActionControlPointCharacteristic:
        return ObjectActionControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC5"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=OACPData(opcode=OACPOpcode.DELETE, parameters=b""),
                description="DELETE opcode with no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00]),
                expected_value=OACPData(
                    opcode=OACPOpcode.READ,
                    parameters=b"\x00\x00\x00\x00\x00\x01\x00\x00",
                ),
                description="READ opcode with offset and length parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x60, 0x05, 0x01]),
                expected_value=OACPData(
                    opcode=OACPOpcode.RESPONSE,
                    parameters=b"\x05\x01",
                ),
                description="RESPONSE opcode with request opcode and result code",
            ),
        ]
