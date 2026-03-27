"""Tests for ReconnectionConfigurationControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.reconnection_configuration_control_point import (
    ReconnectionConfigurationControlPointCharacteristic,
    ReconnectionConfigurationControlPointData,
    ReconnectionConfigurationOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestReconnectionConfigurationControlPointCharacteristic(CommonCharacteristicTests):
    """ReconnectionConfigurationControlPointCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> ReconnectionConfigurationControlPointCharacteristic:
        return ReconnectionConfigurationControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B1F"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=ReconnectionConfigurationControlPointData(
                    op_code=ReconnectionConfigurationOpCode.ENABLE_DISCONNECT,
                    parameter=None,
                ),
                description="Enable disconnect, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0xFF, 0x01]),
                expected_value=ReconnectionConfigurationControlPointData(
                    op_code=ReconnectionConfigurationOpCode.ENABLE_RECONNECT,
                    parameter=b"\xff\x01",
                ),
                description="Enable reconnect with parameter bytes",
            ),
        ]
