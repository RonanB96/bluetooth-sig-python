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
                    opcode=PAMControlPointOpCode.ENQUIRE_SESSIONS,
                    parameter=b"",
                ),
                description="Enquire sessions, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x01, 0x00]),
                expected_value=PhysicalActivityMonitorControlPointData(
                    opcode=PAMControlPointOpCode.START_SESSION_SUB_SESSION,
                    parameter=b"\x01\x00",
                ),
                description="Start session/sub-session with parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=PhysicalActivityMonitorControlPointData(
                    opcode=PAMControlPointOpCode.STOP_SESSION,
                    parameter=b"",
                ),
                description="Stop session, no parameter",
            ),
        ]
