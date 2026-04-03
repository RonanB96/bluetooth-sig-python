"""Tests for ObjectListControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.object_list_control_point import (
    ObjectListControlPointCharacteristic,
    OLCPData,
    OLCPOpcode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestObjectListControlPointCharacteristic(CommonCharacteristicTests):
    """Test Object List Control Point characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> ObjectListControlPointCharacteristic:
        return ObjectListControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AC6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=OLCPData(opcode=OLCPOpcode.FIRST, parameters=b""),
                description="FIRST opcode with no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06, 0x01]),
                expected_value=OLCPData(
                    opcode=OLCPOpcode.ORDER,
                    parameters=b"\x01",
                ),
                description="ORDER opcode with NAME_ASCENDING sort order",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x70, 0x07, 0x01, 0x05, 0x00, 0x00, 0x00]),
                expected_value=OLCPData(
                    opcode=OLCPOpcode.RESPONSE,
                    parameters=b"\x07\x01\x05\x00\x00\x00",
                ),
                description="RESPONSE to REQUEST_NUMBER_OF_OBJECTS with SUCCESS and count",
            ),
        ]
