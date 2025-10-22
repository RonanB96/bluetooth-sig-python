"""Test cycling power control point characteristic parsing."""

import struct

import pytest

from bluetooth_sig.gatt.characteristics import CyclingPowerControlPointCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> bytearray:
        """Valid cycling power control point test data."""
        return bytearray([0x01])  # Set cumulative value command

    def test_cycling_power_control_point_basic(self) -> None:
        """Test basic cycling power control point parsing."""
        char = CyclingPowerControlPointCharacteristic()

        # Test simple op code without parameters
        op_code = 0x03  # Request Supported Sensor Locations
        test_data = struct.pack("<B", op_code)
        result = char.decode_value(bytearray(test_data))

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
        result = char.decode_value(bytearray(test_data))

        assert result.op_code.value == 1
        assert str(result.op_code) == "Set Cumulative Value"
        assert result.cumulative_value == 123456

        # Test Set Crank Length
        op_code = 0x04
        crank_length = 350  # 175.0 mm (350 * 0.5)
        test_data = struct.pack("<BH", op_code, crank_length)
        result = char.decode_value(bytearray(test_data))

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
        result = char.decode_value(bytearray(test_data))

        assert result.op_code.value == 32
        assert str(result.op_code) == "Response Code"
        assert result.request_op_code and result.request_op_code.value == 3
        assert result.response_value and result.response_value.value == 1
        assert str(result.response_value) == "Success"

    def test_cycling_power_control_point_invalid_data(self) -> None:
        """Test cycling power control point with invalid data."""
        char = CyclingPowerControlPointCharacteristic()

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 1 byte"):
            char.decode_value(bytearray())
