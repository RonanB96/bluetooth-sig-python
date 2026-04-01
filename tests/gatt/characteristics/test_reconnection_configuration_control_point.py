"""Tests for Reconnection Configuration Control Point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ReconnectionConfigurationControlPointCharacteristic
from bluetooth_sig.gatt.characteristics.reconnection_configuration_control_point import (
    RCCPOpCode,
    ReconnectionConfigurationControlPointData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestReconnectionConfigurationControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Reconnection Configuration Control Point characteristic."""

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
                    op_code=RCCPOpCode.ENABLE_DISCONNECT,
                    parameter=None,
                ),
                description="Enable Disconnect, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x01, 0x02]),
                expected_value=ReconnectionConfigurationControlPointData(
                    op_code=RCCPOpCode.PROPOSE_SETTINGS,
                    parameter=b"\x01\x02",
                ),
                description="Propose Settings with 2-byte parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0E]),
                expected_value=ReconnectionConfigurationControlPointData(
                    op_code=RCCPOpCode.PROCEDURE_RESPONSE,
                    parameter=None,
                ),
                description="Procedure Response, no parameter",
            ),
        ]

    def test_all_opcodes_valid(self, characteristic: ReconnectionConfigurationControlPointCharacteristic) -> None:
        """Test that all defined opcodes can be decoded."""
        for opcode in RCCPOpCode:
            data = bytearray([int(opcode)])
            result = characteristic.parse_value(data)
            assert result.op_code == opcode

    def test_roundtrip(self, characteristic: ReconnectionConfigurationControlPointCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = ReconnectionConfigurationControlPointData(
            op_code=RCCPOpCode.SET_FILTER_ACCEPT_LIST_TIMER,
            parameter=b"\x10\x27",
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_roundtrip_no_parameter(self, characteristic: ReconnectionConfigurationControlPointCharacteristic) -> None:
        """Test encode/decode roundtrip without parameter."""
        original = ReconnectionConfigurationControlPointData(
            op_code=RCCPOpCode.GET_ACTUAL_COMMUNICATION_PARAMETERS,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
