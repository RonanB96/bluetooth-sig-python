"""Tests for Fitness Machine Control Point characteristic (0x2AD9)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.fitness_machine_control_point import (
    FitnessMachineControlPointCharacteristic,
    FitnessMachineControlPointData,
    FitnessMachineControlPointOpCode,
    FitnessMachineResultCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFitnessMachineControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Fitness Machine Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> FitnessMachineControlPointCharacteristic:
        return FitnessMachineControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AD9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=FitnessMachineControlPointData(
                    op_code=FitnessMachineControlPointOpCode.REQUEST_CONTROL,
                ),
                description="Request control (no params)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x07]),
                expected_value=FitnessMachineControlPointData(
                    op_code=FitnessMachineControlPointOpCode.START_OR_RESUME,
                ),
                description="Start or resume",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x08, 0x01]),
                expected_value=FitnessMachineControlPointData(
                    op_code=FitnessMachineControlPointOpCode.STOP_OR_PAUSE,
                    parameter=b"\x01",
                ),
                description="Stop (param=0x01)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x02, 0x01]),
                expected_value=FitnessMachineControlPointData(
                    op_code=FitnessMachineControlPointOpCode.RESPONSE_CODE,
                    response_op_code=FitnessMachineControlPointOpCode.SET_TARGET_SPEED,
                    result_code=FitnessMachineResultCode.SUCCESS,
                ),
                description="Response: Set Target Speed succeeded",
            ),
        ]

    def test_encode_round_trip_request_control(self) -> None:
        """Verify encode/decode round-trip for request control."""
        char = FitnessMachineControlPointCharacteristic()
        original = FitnessMachineControlPointData(
            op_code=FitnessMachineControlPointOpCode.REQUEST_CONTROL,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_encode_round_trip_response(self) -> None:
        """Verify encode/decode round-trip for response code."""
        char = FitnessMachineControlPointCharacteristic()
        original = FitnessMachineControlPointData(
            op_code=FitnessMachineControlPointOpCode.RESPONSE_CODE,
            response_op_code=FitnessMachineControlPointOpCode.SET_TARGET_POWER,
            result_code=FitnessMachineResultCode.INVALID_PARAMETER,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original

    def test_encode_round_trip_with_parameter(self) -> None:
        """Verify encode/decode round-trip for opcode with parameter."""
        char = FitnessMachineControlPointCharacteristic()
        original = FitnessMachineControlPointData(
            op_code=FitnessMachineControlPointOpCode.STOP_OR_PAUSE,
            parameter=b"\x02",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
