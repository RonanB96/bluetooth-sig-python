"""Tests for SC Control Point characteristic (0x2A55)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.sc_control_point import (
    SCControlPointCharacteristic,
    SCControlPointData,
    SCControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSCControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for SC Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> SCControlPointCharacteristic:
        return SCControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A55"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00, 0x00]),
                expected_value=SCControlPointData(
                    opcode=SCControlPointOpCode.SET_CUMULATIVE_VALUE,
                    parameter=b"\x00\x00\x00\x00",
                ),
                description="Set cumulative value to zero",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=SCControlPointData(
                    opcode=SCControlPointOpCode.START_SENSOR_CALIBRATION,
                    parameter=b"",
                ),
                description="Start sensor calibration (no parameter)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x02]),
                expected_value=SCControlPointData(
                    opcode=SCControlPointOpCode.UPDATE_SENSOR_LOCATION,
                    parameter=b"\x02",
                ),
                description="Update sensor location to value 2",
            ),
        ]
