"""Tests for LN Control Point characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import LNControlPointCharacteristic
from bluetooth_sig.gatt.characteristics.ln_control_point import (
    LNControlPointData,
    LNControlPointOpCode,
    LNControlPointResponseValue,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLNControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for LN Control Point characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Only adds LN control point-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> LNControlPointCharacteristic:
        """Return a LN Control Point characteristic instance."""
        return LNControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for LN Control Point characteristic."""
        return "2A6B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for LN control point (set cumulative value request)."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0xE8, 0x03, 0x00, 0x00]),  # SET_CUMULATIVE_VALUE, value=1000
                expected_value=LNControlPointData(
                    op_code=LNControlPointOpCode.SET_CUMULATIVE_VALUE,
                    cumulative_value=1000,
                    content_mask=None,
                    navigation_control_value=None,
                    route_number=None,
                    route_name=None,
                    fix_rate=None,
                    elevation=None,
                    request_op_code=None,
                    response_value=None,
                    response_parameter=None,
                ),
                description="LN Control Point set cumulative value to 1000",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x01]),  # NAVIGATION_CONTROL, start navigation
                expected_value=LNControlPointData(
                    op_code=LNControlPointOpCode.NAVIGATION_CONTROL,
                    cumulative_value=None,
                    content_mask=None,
                    navigation_control_value=1,
                    route_number=None,
                    route_name=None,
                    fix_rate=None,
                    elevation=None,
                    request_op_code=None,
                    response_value=None,
                    response_parameter=None,
                ),
                description="LN Control Point start navigation",
            ),
        ]

    # === LN Control Point-Specific Tests ===
    @pytest.mark.parametrize(
        "data,expected",
        [
            # Set cumulative value
            (
                bytearray([0x01, 0x00, 0x00, 0x00, 0x00]),  # SET_CUMULATIVE_VALUE, value=0
                {
                    "op_code": "SET_CUMULATIVE_VALUE",
                    "cumulative_value": 0,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Mask location and speed content
            (
                bytearray([0x02, 0xFF, 0xFF]),  # MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT, mask=0xFFFF
                {
                    "op_code": "MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT",
                    "cumulative_value": None,
                    "content_mask": 0xFFFF,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Navigation control - start
            (
                bytearray([0x03, 0x01]),  # NAVIGATION_CONTROL, start
                {
                    "op_code": "NAVIGATION_CONTROL",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": 0x01,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Navigation control - stop
            (
                bytearray([0x03, 0x00]),  # NAVIGATION_CONTROL, stop
                {
                    "op_code": "NAVIGATION_CONTROL",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": 0x00,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Request number of routes
            (
                bytearray([0x04]),  # REQUEST_NUMBER_OF_ROUTES
                {
                    "op_code": "REQUEST_NUMBER_OF_ROUTES",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Request name of route
            (
                bytearray([0x05, 0x01]),  # REQUEST_NAME_OF_ROUTE, route_number=1
                {
                    "op_code": "REQUEST_NAME_OF_ROUTE",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": 1,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Select route
            (
                bytearray([0x06, 0x02]),  # SELECT_ROUTE, route_number=2
                {
                    "op_code": "SELECT_ROUTE",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": 2,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Set fix rate
            (
                bytearray([0x07, 0x01]),  # SET_FIX_RATE, fix_rate=1
                {
                    "op_code": "SET_FIX_RATE",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": 1,
                    "elevation": None,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Set elevation
            (
                bytearray([0x08, 0x00, 0x00, 0x00, 0x00]),  # SET_ELEVATION, elevation=0
                {
                    "op_code": "SET_ELEVATION",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": 0.0,
                    "request_op_code": None,
                    "response_value": None,
                    "response_parameter": None,
                },
            ),
            # Response - success
            (
                bytearray([0x20, 0x01, 0x01]),  # RESPONSE_CODE, request=SET_CUMULATIVE_VALUE, response=SUCCESS
                {
                    "op_code": "RESPONSE_CODE",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": "SET_CUMULATIVE_VALUE",
                    "response_value": "SUCCESS",
                    "response_parameter": None,
                },
            ),
            # Response - op code not supported
            (
                bytearray(
                    [0x20, 0x02, 0x02, 0xFF, 0x00, 0x00, 0x00]
                ),  # RESPONSE_CODE, request=MASK_..., response=OP_CODE_NOT_SUPPORTED, param=255
                {
                    "op_code": "RESPONSE_CODE",
                    "cumulative_value": None,
                    "content_mask": None,
                    "navigation_control_value": None,
                    "route_number": None,
                    "route_name": None,
                    "fix_rate": None,
                    "elevation": None,
                    "request_op_code": "MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT",
                    "response_value": "OP_CODE_NOT_SUPPORTED",
                    "response_parameter": 255,
                },
            ),
        ],
    )
    def test_ln_control_point_various_operations(
        self, characteristic: LNControlPointCharacteristic, data: bytearray, expected: dict[str, Any]
    ) -> None:
        """Test LN control point with various operations."""
        result = characteristic.parse_value(data)
        for field, expected_value in expected.items():
            actual_value = getattr(result, field)
            if expected_value is not None and isinstance(expected_value, str):
                # Convert enum to name for comparison
                actual_name = actual_value.name if hasattr(actual_value, "name") else str(actual_value)
                assert actual_name == expected_value, f"Field {field}: expected {expected_value}, got {actual_name}"
            else:
                assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"

    def test_ln_control_point_response_success(self, characteristic: LNControlPointCharacteristic) -> None:
        """Test LN control point response with success code."""
        data = bytearray(
            [
                0x20,  # op_code (RESPONSE_CODE)
                0x01,  # request_op_code (SET_CUMULATIVE_VALUE)
                0x01,  # response_value (SUCCESS)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.op_code == LNControlPointOpCode.RESPONSE_CODE
        assert result.request_op_code == LNControlPointOpCode.SET_CUMULATIVE_VALUE
        assert result.response_value == LNControlPointResponseValue.SUCCESS
        assert result.response_parameter is None

    def test_ln_control_point_response_with_parameter(self, characteristic: LNControlPointCharacteristic) -> None:
        """Test LN control point response with parameter."""
        data = bytearray(
            [
                0x20,  # op_code (RESPONSE_CODE)
                0x02,  # request_op_code (MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT)
                0x02,  # response_value (OP_CODE_NOT_SUPPORTED)
                0xFF,
                0x00,
                0x00,
                0x00,  # response_parameter (255)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.op_code == LNControlPointOpCode.RESPONSE_CODE
        assert result.request_op_code == LNControlPointOpCode.MASK_LOCATION_AND_SPEED_CHARACTERISTIC_CONTENT
        assert result.response_value == LNControlPointResponseValue.OP_CODE_NOT_SUPPORTED
        assert result.response_parameter == 255

    def test_ln_control_point_start_navigation_request(self, characteristic: LNControlPointCharacteristic) -> None:
        """Test LN control point start navigation request."""
        data = bytearray(
            [
                0x03,  # op_code (NAVIGATION_CONTROL)
                0x01,  # navigation_control_value (start navigation)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.op_code == LNControlPointOpCode.NAVIGATION_CONTROL
        assert result.navigation_control_value == 0x01

    def test_ln_control_point_stop_navigation_request(self, characteristic: LNControlPointCharacteristic) -> None:
        """Test LN control point stop navigation request."""
        data = bytearray(
            [
                0x03,  # op_code (NAVIGATION_CONTROL)
                0x00,  # navigation_control_value (stop navigation)
            ]
        )

        result = characteristic.parse_value(data)
        assert result.op_code == LNControlPointOpCode.NAVIGATION_CONTROL
        assert result.navigation_control_value == 0x00
