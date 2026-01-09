"""Test cycling power control point characteristic parsing."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics.cycling_power_control_point import (
    CyclingPowerControlPointCharacteristic,
    CyclingPowerControlPointData,
    CyclingPowerOpCode,
    CyclingPowerResponseValue,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCyclingPowerControlPointCharacteristic(CommonCharacteristicTests):
    """Test Cycling Power Control Point characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> CyclingPowerControlPointCharacteristic:
        """Provide Cycling Power Control Point characteristic for testing."""
        return CyclingPowerControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Cycling Power Control Point characteristic."""
        return "2A66"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid cycling power control point test data covering various op codes and parameters."""
        return [
            # Test 1: Set Cumulative Value with parameter
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x40, 0xE2, 0x01, 0x00]),  # op_code + 123456 (little endian)
                expected_value=CyclingPowerControlPointData(
                    op_code=CyclingPowerOpCode.SET_CUMULATIVE_VALUE,
                    cumulative_value=123456,
                    sensor_location=None,
                    crank_length=None,
                    chain_length=None,
                    chain_weight=None,
                    span_length=None,
                    measurement_mask=None,
                    request_op_code=None,
                    response_value=None,
                ),
                description="Set cumulative value with parameter",
            ),
            # Test 2: Update Sensor Location
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x05]),  # op_code + location
                expected_value=CyclingPowerControlPointData(
                    op_code=CyclingPowerOpCode.UPDATE_SENSOR_LOCATION,
                    cumulative_value=None,
                    sensor_location=5,
                    crank_length=None,
                    chain_length=None,
                    chain_weight=None,
                    span_length=None,
                    measurement_mask=None,
                    request_op_code=None,
                    response_value=None,
                ),
                description="Update sensor location",
            ),
            # Test 3: Set Crank Length
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x5E, 0x01]),  # op_code + 350 (175.0mm * 2)
                expected_value=CyclingPowerControlPointData(
                    op_code=CyclingPowerOpCode.SET_CRANK_LENGTH,
                    cumulative_value=None,
                    sensor_location=None,
                    crank_length=175.0,
                    chain_length=None,
                    chain_weight=None,
                    span_length=None,
                    measurement_mask=None,
                    request_op_code=None,
                    response_value=None,
                ),
                description="Set crank length to 175.0mm",
            ),
            # Test 4: Set Chain Weight
            CharacteristicTestData(
                input_data=bytearray([0x08, 0xF4, 0x01]),  # op_code + 500 (50.0g * 10)
                expected_value=CyclingPowerControlPointData(
                    op_code=CyclingPowerOpCode.SET_CHAIN_WEIGHT,
                    cumulative_value=None,
                    sensor_location=None,
                    crank_length=None,
                    chain_length=None,
                    chain_weight=50.0,
                    span_length=None,
                    measurement_mask=None,
                    request_op_code=None,
                    response_value=None,
                ),
                description="Set chain weight to 50.0g",
            ),
            # Test 5: Response Code
            CharacteristicTestData(
                input_data=bytearray([0x20, 0x03, 0x01]),  # Response + request_op + success
                expected_value=CyclingPowerControlPointData(
                    op_code=CyclingPowerOpCode.RESPONSE_CODE,
                    cumulative_value=None,
                    sensor_location=None,
                    crank_length=None,
                    chain_length=None,
                    chain_weight=None,
                    span_length=None,
                    measurement_mask=None,
                    request_op_code=CyclingPowerOpCode.REQUEST_SUPPORTED_SENSOR_LOCATIONS,
                    response_value=CyclingPowerResponseValue.SUCCESS,
                ),
                description="Response code with success",
            ),
            # Test 6: Simple op code only (no parameters)
            CharacteristicTestData(
                input_data=bytearray([0x03]),  # Request Supported Sensor Locations
                expected_value=CyclingPowerControlPointData(
                    op_code=CyclingPowerOpCode.REQUEST_SUPPORTED_SENSOR_LOCATIONS,
                    cumulative_value=None,
                    sensor_location=None,
                    crank_length=None,
                    chain_length=None,
                    chain_weight=None,
                    span_length=None,
                    measurement_mask=None,
                    request_op_code=None,
                    response_value=None,
                ),
                description="Request supported sensor locations (no parameters)",
            ),
        ]

    def test_cycling_power_control_point_basic(self) -> None:
        """Test basic cycling power control point parsing."""
        char = CyclingPowerControlPointCharacteristic()

        # Test simple op code without parameters
        op_code = 0x03  # Request Supported Sensor Locations
        test_data = struct.pack("<B", op_code)
        result = char.parse_value(bytearray(test_data))
        assert result is not None

        assert result.op_code.value == 3
        assert str(result.op_code) == "Request Supported Sensor Locations"
        assert result.cumulative_value is None
        assert result.sensor_location is None

    def test_cycling_power_control_point_with_parameters(self) -> None:
        """Test cycling power control point with parameters."""
        char = CyclingPowerControlPointCharacteristic()

        # Test Set Cumulative Value
        op_code = 0x01
        cumulative_value = 123456
        test_data = struct.pack("<BI", op_code, cumulative_value)
        result = char.parse_value(bytearray(test_data))
        assert result is not None

        assert result.op_code.value == 1
        assert str(result.op_code) == "Set Cumulative Value"
        assert result.cumulative_value == 123456

        # Test Set Crank Length
        op_code = 0x04
        crank_length = 350  # 175.0 mm (350 * 0.5)
        test_data = struct.pack("<BH", op_code, crank_length)
        result = char.parse_value(bytearray(test_data))
        assert result is not None

        assert result.op_code.value == 4
        assert str(result.op_code) == "Set Crank Length"
        assert result.crank_length == 175.0

    def test_cycling_power_control_point_response(self) -> None:
        """Test cycling power control point response parsing."""
        char = CyclingPowerControlPointCharacteristic()

        # Test response code
        op_code = 0x20  # Response Code
        request_op_code = 0x03  # Original request
        response_value = 0x01  # Success
        test_data = struct.pack("<BBB", op_code, request_op_code, response_value)
        result = char.parse_value(bytearray(test_data))
        assert result is not None

        assert result.op_code.value == 32
        assert str(result.op_code) == "Response Code"
        assert result.request_op_code and result.request_op_code.value == 3
        assert result.response_value and result.response_value.value == 1
        assert str(result.response_value) == "Success"

    def test_cycling_power_control_point_invalid_data(self) -> None:
        """Test cycling power control point with invalid data."""
        char = CyclingPowerControlPointCharacteristic()

        # Test empty data
        with pytest.raises(CharacteristicParseError) as exc_info:
            char.parse_value(bytearray())
        assert "expected at least 1 bytes, got 0" in str(exc_info.value)
