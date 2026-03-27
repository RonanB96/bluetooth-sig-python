"""Tests for PhysicalActivityMonitorControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.physical_activity_monitor_control_point import (
    PAMControlPointOpCode,
    PhysicalActivityMonitorControlPointCharacteristic,
    PhysicalActivityMonitorControlPointData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPhysicalActivityMonitorControlPointCharacteristic(CommonCharacteristicTests):
    """PhysicalActivityMonitorControlPointCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> PhysicalActivityMonitorControlPointCharacteristic:
        return PhysicalActivityMonitorControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B43"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=PhysicalActivityMonitorControlPointData(
                    opcode=PAMControlPointOpCode.START_SESSION,
                    parameter=b"",
                ),
                description="Start session, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x02]),
                expected_value=PhysicalActivityMonitorControlPointData(
                    opcode=PAMControlPointOpCode.SET_ACTIVITY_TYPE,
                    parameter=b"\x02",
                ),
                description="Set activity type with parameter",
            ),
        ]
