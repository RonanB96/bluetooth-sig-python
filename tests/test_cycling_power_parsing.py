"""Test cycling power service and characteristics parsing."""

import struct

import pytest

from bluetooth_sig.gatt.characteristics import (
    CyclingPowerControlPointCharacteristic,
    CyclingPowerFeatureCharacteristic,
    CyclingPowerMeasurementCharacteristic,
    CyclingPowerVectorCharacteristic,
)


class TestCyclingPowerParsing:
    """Test cycling power data parsing functionality."""

    def test_cycling_power_feature_parsing(self):
        """Test cycling power feature characteristic parsing."""
        char = CyclingPowerFeatureCharacteristic()

        # Test basic feature mask
        feature_data = struct.pack("<I", 0x0000001F)  # Multiple features enabled
        result = char.decode_value(bytearray(feature_data))
        assert result == 31
        assert char.unit == ""

        # Test single feature
        feature_data = struct.pack("<I", 0x00000001)  # Only pedal power balance
        result = char.decode_value(bytearray(feature_data))
        assert result == 1

        # Test no features
        feature_data = struct.pack("<I", 0x00000000)
        result = char.decode_value(bytearray(feature_data))
        assert result == 0

    def test_cycling_power_feature_invalid_data(self):
        """Test cycling power feature with invalid data."""
        char = CyclingPowerFeatureCharacteristic()

        # Test insufficient data
        with pytest.raises(ValueError, match="must be at least 4 bytes"):
            char.decode_value(bytearray([0x01, 0x02]))

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 4 bytes"):
            char.decode_value(bytearray())

    def test_cycling_power_measurement_basic(self):
        """Test basic cycling power measurement parsing."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test minimum required data: Flags(2) + Power(2)
        flags = 0x0000  # No optional fields
        power = 250  # 250 watts
        test_data = struct.pack("<Hh", flags, power)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 0
        assert result.instantaneous_power == 250
        assert char.unit == "W"

    def test_cycling_power_measurement_with_pedal_balance(self):
        """Test cycling power measurement with pedal power balance."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test with pedal power balance
        flags = 0x0001  # Pedal power balance present
        power = 300
        balance = 100  # 50% (100 * 0.5%)
        test_data = struct.pack("<HhB", flags, power, balance)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 1
        assert result.instantaneous_power == 300
        assert result.pedal_power_balance == 50.0

        # Test with unknown balance value (0xFF)
        balance = 0xFF
        test_data = struct.pack("<HhB", flags, power, balance)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 1
        assert result.instantaneous_power == 300
        assert result.pedal_power_balance is None  # No balance when unknown

    def test_cycling_power_measurement_with_accumulated_energy(self):
        """Test cycling power measurement with accumulated energy."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test with accumulated energy
        flags = 0x0008  # Accumulated energy present
        power = 280
        energy = 150  # 150 kJ
        test_data = struct.pack("<HhH", flags, power, energy)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 8
        assert result.instantaneous_power == 280
        assert result.accumulated_energy == 150

    def test_cycling_power_measurement_with_wheel_data(self):
        """Test cycling power measurement with wheel revolution data."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test with wheel revolution data
        flags = 0x0010  # Wheel revolution data present
        power = 320
        wheel_revs = 12345
        wheel_time = 2048  # 1 second in 1/2048 units
        test_data = struct.pack("<HhIH", flags, power, wheel_revs, wheel_time)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 16
        assert result.instantaneous_power == 320
        assert result.cumulative_wheel_revolutions == 12345
        assert result.last_wheel_event_time == 1.0  # 2048 / 2048 = 1.0 second

    def test_cycling_power_measurement_with_crank_data(self):
        """Test cycling power measurement with crank revolution data."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test with crank revolution data
        flags = 0x0020  # Crank revolution data present
        power = 350
        crank_revs = 5678
        crank_time = 1024  # 1 second in 1/1024 units
        test_data = struct.pack("<HhHH", flags, power, crank_revs, crank_time)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 32
        assert result.instantaneous_power == 350
        assert result.cumulative_crank_revolutions == 5678
        assert result.last_crank_event_time == 1.0  # 1024 / 1024 = 1.0 second

    def test_cycling_power_measurement_combined_fields(self):
        """Test cycling power measurement with multiple optional fields."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test with pedal balance + accumulated energy + crank data
        flags = 0x0001 | 0x0008 | 0x0020  # Multiple flags
        power = 400
        balance = 120  # 60%
        energy = 200  # 200 kJ
        crank_revs = 8900
        crank_time = 512  # 0.5 second
        test_data = struct.pack("<HhBHHH", flags, power, balance, energy, crank_revs, crank_time)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 41  # 0x0001 | 0x0008 | 0x0020 = 1 + 8 + 32 = 41
        assert result.instantaneous_power == 400
        assert result.pedal_power_balance == 60.0
        assert result.accumulated_energy == 200
        assert result.cumulative_crank_revolutions == 8900
        assert result.last_crank_event_time == 0.5

    def test_cycling_power_measurement_invalid_data(self):
        """Test cycling power measurement with invalid data."""
        char = CyclingPowerMeasurementCharacteristic()

        # Test insufficient data
        with pytest.raises(ValueError, match="must be at least 4 bytes"):
            char.decode_value(bytearray([0x01, 0x02]))

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 4 bytes"):
            char.decode_value(bytearray())

    def test_cycling_power_vector_basic(self):
        """Test basic cycling power vector parsing."""
        char = CyclingPowerVectorCharacteristic()

        # Test minimum required data: Flags(1) + Crank Revs(2) + Crank Time(2) + First Angle(2)
        flags = 0x00  # No optional arrays
        crank_revs = 1234
        crank_time = 1024  # 1 second
        first_angle = 90  # 0.5 degrees (90 / 180)
        test_data = struct.pack("<BHHH", flags, crank_revs, crank_time, first_angle)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 0
        assert result.crank_revolution_data.crank_revolutions == 1234
        assert result.crank_revolution_data.last_crank_event_time == 1.0
        assert result.first_crank_measurement_angle == 0.5
        assert char.unit == "various"

    def test_cycling_power_vector_with_force_array(self):
        """Test cycling power vector with force magnitude array."""
        char = CyclingPowerVectorCharacteristic()

        # Test with force magnitude array
        flags = 0x01  # Force magnitudes present
        crank_revs = 1234
        crank_time = 1024  # 1 second
        first_angle = 180  # 1.0 degrees
        force1 = 100  # 100 N
        force2 = 150  # 150 N
        test_data = struct.pack("<BHHHhh", flags, crank_revs, crank_time, first_angle, force1, force2)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 1
        assert result.crank_revolution_data.crank_revolutions == 1234
        assert result.crank_revolution_data.last_crank_event_time == 1.0
        assert result.first_crank_measurement_angle == 1.0
        assert result.instantaneous_force_magnitude_array == (100.0, 150.0)

    def test_cycling_power_vector_with_torque_array(self):
        """Test cycling power vector with torque magnitude array."""
        char = CyclingPowerVectorCharacteristic()

        # Test with torque magnitude array
        flags = 0x02  # Torque magnitudes present
        crank_revs = 1234
        crank_time = 1024  # 1 second
        first_angle = 360  # 2.0 degrees
        torque1 = 160  # 5.0 Nm (160 / 32)
        torque2 = 192  # 6.0 Nm (192 / 32)
        test_data = struct.pack("<BHHHhh", flags, crank_revs, crank_time, first_angle, torque1, torque2)
        result = char.decode_value(bytearray(test_data))

        assert result.flags == 2
        assert result.crank_revolution_data.crank_revolutions == 1234
        assert result.crank_revolution_data.last_crank_event_time == 1.0
        assert result.first_crank_measurement_angle == 2.0
        assert result.instantaneous_torque_magnitude_array == (5.0, 6.0)

    def test_cycling_power_vector_invalid_data(self):
        """Test cycling power vector with invalid data."""
        char = CyclingPowerVectorCharacteristic()

        # Test insufficient data
        with pytest.raises(ValueError, match="must be at least 7 bytes"):
            char.decode_value(bytearray([0x01, 0x02, 0x03]))

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 7 bytes"):
            char.decode_value(bytearray())

    def test_cycling_power_control_point_basic(self):
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

    def test_cycling_power_control_point_with_parameters(self):
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

    def test_cycling_power_control_point_response(self):
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

    def test_cycling_power_control_point_invalid_data(self):
        """Test cycling power control point with invalid data."""
        char = CyclingPowerControlPointCharacteristic()

        # Test empty data
        with pytest.raises(ValueError, match="must be at least 1 byte"):
            char.decode_value(bytearray())
