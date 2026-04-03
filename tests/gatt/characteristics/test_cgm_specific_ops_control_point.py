"""Tests for CGM Specific Ops Control Point characteristic (0x2AAC)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.cgm_specific_ops_control_point import (
    CGMSpecificOpsControlPointCharacteristic,
    CGMSpecificOpsControlPointData,
    CGMSpecificOpsOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCGMSpecificOpsControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for CGM Specific Ops Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> CGMSpecificOpsControlPointCharacteristic:
        return CGMSpecificOpsControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AAC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x05]),
                expected_value=CGMSpecificOpsControlPointData(
                    opcode=CGMSpecificOpsOpCode.SET_CGM_COMMUNICATION_INTERVAL,
                    operand=b"\x05",
                ),
                description="Set communication interval to 5 minutes",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x1A]),
                expected_value=CGMSpecificOpsControlPointData(
                    opcode=CGMSpecificOpsOpCode.START_THE_SESSION,
                    operand=b"",
                ),
                description="Start session (no operand)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x1C, 0x01, 0x01]),
                expected_value=CGMSpecificOpsControlPointData(
                    opcode=CGMSpecificOpsOpCode.RESPONSE_CODE,
                    operand=b"\x01\x01",
                ),
                description="Response code: success for Set Communication Interval",
            ),
        ]
