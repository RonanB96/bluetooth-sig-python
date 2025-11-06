"""Tests for Nordic Thingy:52 vendor characteristic adapters."""

from __future__ import annotations

import struct

import pytest

from examples.vendor_characteristics import (
    ThingyButtonData,
    ThingyColorData,
    ThingyEulerData,
    ThingyGasData,
    ThingyGravityVectorData,
    ThingyHeadingData,
    ThingyHumidityData,
    ThingyPressureData,
    ThingyQuaternionData,
    ThingyRawMotionData,
    ThingyRotationMatrixData,
    ThingyStepCounterData,
    ThingyTapData,
    ThingyTemperatureData,
    decode_thingy_button,
    decode_thingy_color,
    decode_thingy_euler,
    decode_thingy_gas,
    decode_thingy_gravity_vector,
    decode_thingy_heading,
    decode_thingy_humidity,
    decode_thingy_orientation,
    decode_thingy_pressure,
    decode_thingy_quaternion,
    decode_thingy_raw_motion,
    decode_thingy_rotation_matrix,
    decode_thingy_step_counter,
    decode_thingy_tap,
    decode_thingy_temperature,
)


class TestThingyTemperature:
    """Test Thingy:52 temperature characteristic decoder."""

    def test_decode_valid_temperature(self) -> None:
        """Test decoding valid temperature value."""
        # 23.50°C
        data = bytes([0x17, 0x32])
        result = decode_thingy_temperature(data)

        assert isinstance(result, ThingyTemperatureData)
        assert result.temperature_celsius == 23
        assert result.temperature_decimal == 50

    def test_decode_negative_temperature(self) -> None:
        """Test decoding negative temperature value."""
        # -5.25°C
        data = bytes([0xFB, 0x19])  # -5 (signed int8), 25
        result = decode_thingy_temperature(data)

        assert result.temperature_celsius == -5
        assert result.temperature_decimal == 25

    def test_decode_zero_temperature(self) -> None:
        """Test decoding zero temperature."""
        # 0.00°C
        data = bytes([0x00, 0x00])
        result = decode_thingy_temperature(data)

        assert result.temperature_celsius == 0
        assert result.temperature_decimal == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x17])  # Only 1 byte

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_temperature(data)

        assert "must be 2 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x17, 0x32, 0xFF])  # 3 bytes

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_temperature(data)

        assert "must be 2 bytes" in str(exc_info.value).lower()

    def test_decode_invalid_decimal(self) -> None:
        """Test error on invalid decimal value."""
        # Decimal part > 99
        data = bytes([0x17, 0x64])  # 100 is invalid

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_temperature(data)

        assert "decimal must be 0-99" in str(exc_info.value).lower()


class TestThingyPressure:
    """Test Thingy:52 pressure characteristic decoder."""

    def test_decode_valid_pressure(self) -> None:
        """Test decoding valid pressure value."""
        # 101088.50 Pa
        data = bytes([0xE0, 0x8A, 0x01, 0x00, 0x32])
        result = decode_thingy_pressure(data)

        assert isinstance(result, ThingyPressureData)
        assert result.pressure_integer == 101088
        assert result.pressure_decimal == 50

    def test_decode_zero_pressure(self) -> None:
        """Test decoding zero pressure."""
        data = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
        result = decode_thingy_pressure(data)

        assert result.pressure_integer == 0
        assert result.pressure_decimal == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0xE0, 0x8A, 0x01, 0x00])  # Only 4 bytes

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_pressure(data)

        assert "must be 5 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0xE0, 0x8A, 0x01, 0x00, 0x32, 0xFF])  # 6 bytes

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_pressure(data)

        assert "must be 5 bytes" in str(exc_info.value).lower()

    def test_decode_invalid_decimal(self) -> None:
        """Test error on invalid decimal value."""
        # Decimal part > 99
        data = bytes([0xE0, 0x8A, 0x01, 0x00, 0x64])  # 100 is invalid

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_pressure(data)

        assert "decimal must be 0-99" in str(exc_info.value).lower()


class TestThingyHumidity:
    """Test Thingy:52 humidity characteristic decoder."""

    def test_decode_valid_humidity(self) -> None:
        """Test decoding valid humidity value."""
        # 65%
        data = bytes([0x41])
        result = decode_thingy_humidity(data)

        assert isinstance(result, ThingyHumidityData)
        assert result.humidity_percent == 65

    def test_decode_boundary_values(self) -> None:
        """Test decoding boundary humidity values."""
        # 0%
        result_min = decode_thingy_humidity(bytes([0x00]))
        assert result_min.humidity_percent == 0

        # 100%
        result_max = decode_thingy_humidity(bytes([0x64]))
        assert result_max.humidity_percent == 100

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_humidity(data)

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x41, 0xFF])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_humidity(data)

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_out_of_range(self) -> None:
        """Test error on out-of-range value."""
        # Humidity > 100%
        data = bytes([0x65])  # 101%

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_humidity(data)

        assert "must be 0-100" in str(exc_info.value).lower()


class TestThingyGas:
    """Test Thingy:52 gas characteristic decoder."""

    def test_decode_valid_gas(self) -> None:
        """Test decoding valid gas sensor values."""
        # eCO2: 400 ppm, TVOC: 50 ppb
        data = bytes([0x90, 0x01, 0x32, 0x00])
        result = decode_thingy_gas(data)

        assert isinstance(result, ThingyGasData)
        assert result.eco2_ppm == 400
        assert result.tvoc_ppb == 50

    def test_decode_zero_gas(self) -> None:
        """Test decoding zero gas values."""
        data = bytes([0x00, 0x00, 0x00, 0x00])
        result = decode_thingy_gas(data)

        assert result.eco2_ppm == 0
        assert result.tvoc_ppb == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x90, 0x01, 0x32])  # Only 3 bytes

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_gas(data)

        assert "must be 4 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x90, 0x01, 0x32, 0x00, 0xFF])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_gas(data)

        assert "must be 4 bytes" in str(exc_info.value).lower()


class TestThingyColor:
    """Test Thingy:52 color characteristic decoder."""

    def test_decode_valid_color(self) -> None:
        """Test decoding valid color values."""
        # R: 255, G: 128, B: 64, C: 256
        data = bytes([0xFF, 0x00, 0x80, 0x00, 0x40, 0x00, 0x00, 0x01])
        result = decode_thingy_color(data)

        assert isinstance(result, ThingyColorData)
        assert result.red == 255
        assert result.green == 128
        assert result.blue == 64
        assert result.clear == 256

    def test_decode_zero_color(self) -> None:
        """Test decoding zero color values."""
        data = bytes([0x00] * 8)
        result = decode_thingy_color(data)

        assert result.red == 0
        assert result.green == 0
        assert result.blue == 0
        assert result.clear == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0xFF, 0x00, 0x80, 0x00, 0x40, 0x00, 0x00])  # 7 bytes

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_color(data)

        assert "must be 8 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0xFF] * 9)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_color(data)

        assert "must be 8 bytes" in str(exc_info.value).lower()


class TestThingyButton:
    """Test Thingy:52 button characteristic decoder."""

    def test_decode_button_pressed(self) -> None:
        """Test decoding button pressed state."""
        data = bytes([0x01])
        result = decode_thingy_button(data)

        assert isinstance(result, ThingyButtonData)
        assert result.pressed is True

    def test_decode_button_released(self) -> None:
        """Test decoding button released state."""
        data = bytes([0x00])
        result = decode_thingy_button(data)

        assert result.pressed is False

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_button(data)

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x01, 0xFF])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_button(data)

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_invalid_state(self) -> None:
        """Test error on invalid button state."""
        data = bytes([0x02])  # Invalid state

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_button(data)

        assert "must be 0 or 1" in str(exc_info.value).lower()


class TestThingyTap:
    """Test Thingy:52 tap characteristic decoder."""

    def test_decode_valid_tap(self) -> None:
        """Test decoding valid tap data."""
        # y+ direction, 3 taps
        data = bytes([0x02, 0x03])
        result = decode_thingy_tap(data)

        assert isinstance(result, ThingyTapData)
        assert result.direction == 2
        assert result.count == 3

    def test_decode_boundary_directions(self) -> None:
        """Test decoding boundary tap directions."""
        # Direction 0 (x+)
        result_min = decode_thingy_tap(bytes([0x00, 0x01]))
        assert result_min.direction == 0

        # Direction 5 (z-)
        result_max = decode_thingy_tap(bytes([0x05, 0x01]))
        assert result_max.direction == 5

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x02])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_tap(data)

        assert "must be 2 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x02, 0x03, 0xFF])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_tap(data)

        assert "must be 2 bytes" in str(exc_info.value).lower()

    def test_decode_invalid_direction(self) -> None:
        """Test error on invalid tap direction."""
        data = bytes([0x06, 0x01])  # Direction > 5

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_tap(data)

        assert "must be 0-5" in str(exc_info.value).lower()


class TestThingyOrientation:
    """Test Thingy:52 orientation characteristic decoder."""

    def test_decode_valid_orientation(self) -> None:
        """Test decoding valid orientation values."""
        # Portrait
        result_portrait = decode_thingy_orientation(bytes([0x00]))
        assert result_portrait.orientation == 0

        # Landscape
        result_landscape = decode_thingy_orientation(bytes([0x01]))
        assert result_landscape.orientation == 1

        # Reverse portrait
        result_reverse = decode_thingy_orientation(bytes([0x02]))
        assert result_reverse.orientation == 2

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_orientation(data)

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x01, 0xFF])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_orientation(data)

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_invalid_orientation(self) -> None:
        """Test error on invalid orientation value."""
        data = bytes([0x03])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_orientation(data)

        assert "must be 0-2" in str(exc_info.value).lower()


class TestThingyQuaternion:
    """Test Thingy:52 quaternion characteristic decoder."""

    def test_decode_valid_quaternion(self) -> None:
        """Test decoding valid quaternion values."""
        # All zeros
        data = bytes([0x00] * 16)
        result = decode_thingy_quaternion(data)

        assert isinstance(result, ThingyQuaternionData)
        assert result.w == 0
        assert result.x == 0
        assert result.y == 0
        assert result.z == 0

    def test_decode_non_zero_quaternion(self) -> None:
        """Test decoding non-zero quaternion."""
        # w=1000, x=2000, y=3000, z=4000 (little-endian int32)
        data = struct.pack("<iiii", 1000, 2000, 3000, 4000)
        result = decode_thingy_quaternion(data)

        assert result.w == 1000
        assert result.x == 2000
        assert result.y == 3000
        assert result.z == 4000

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x00] * 15)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_quaternion(data)

        assert "must be 16 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x00] * 17)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_quaternion(data)

        assert "must be 16 bytes" in str(exc_info.value).lower()


class TestThingyStepCounter:
    """Test Thingy:52 step counter characteristic decoder."""

    def test_decode_valid_step_counter(self) -> None:
        """Test decoding valid step counter data."""
        # 100 steps, 10000 ms
        data = bytes([0x64, 0x00, 0x00, 0x00, 0x10, 0x27, 0x00, 0x00])
        result = decode_thingy_step_counter(data)

        assert isinstance(result, ThingyStepCounterData)
        assert result.steps == 100
        assert result.time_ms == 10000

    def test_decode_zero_step_counter(self) -> None:
        """Test decoding zero step counter."""
        data = bytes([0x00] * 8)
        result = decode_thingy_step_counter(data)

        assert result.steps == 0
        assert result.time_ms == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x64, 0x00, 0x00, 0x00, 0x10, 0x27, 0x00])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_step_counter(data)

        assert "must be 8 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x64] * 9)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_step_counter(data)

        assert "must be 8 bytes" in str(exc_info.value).lower()


class TestThingyRawMotion:
    """Test Thingy:52 raw motion characteristic decoder."""

    def test_decode_valid_raw_motion(self) -> None:
        """Test decoding valid raw motion data."""
        data = bytes([0x00] * 18)
        result = decode_thingy_raw_motion(data)

        assert isinstance(result, ThingyRawMotionData)
        assert result.accel_x == 0
        assert result.accel_y == 0
        assert result.accel_z == 0
        assert result.gyro_x == 0
        assert result.gyro_y == 0
        assert result.gyro_z == 0
        assert result.compass_x == 0
        assert result.compass_y == 0
        assert result.compass_z == 0

    def test_decode_non_zero_raw_motion(self) -> None:
        """Test decoding non-zero raw motion data."""
        # Accel: (100, 200, 300), Gyro: (400, 500, 600), Compass: (700, 800, 900)
        data = struct.pack("<hhhhhhhhh", 100, 200, 300, 400, 500, 600, 700, 800, 900)
        result = decode_thingy_raw_motion(data)

        assert result.accel_x == 100
        assert result.accel_y == 200
        assert result.accel_z == 300
        assert result.gyro_x == 400
        assert result.gyro_y == 500
        assert result.gyro_z == 600
        assert result.compass_x == 700
        assert result.compass_y == 800
        assert result.compass_z == 900

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x00] * 17)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_raw_motion(data)

        assert "must be 18 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x00] * 19)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_raw_motion(data)

        assert "must be 18 bytes" in str(exc_info.value).lower()


class TestThingyEuler:
    """Test Thingy:52 Euler angles characteristic decoder."""

    def test_decode_valid_euler(self) -> None:
        """Test decoding valid Euler angles."""
        data = bytes([0x00] * 12)
        result = decode_thingy_euler(data)

        assert isinstance(result, ThingyEulerData)
        assert result.roll == 0
        assert result.pitch == 0
        assert result.yaw == 0

    def test_decode_non_zero_euler(self) -> None:
        """Test decoding non-zero Euler angles."""
        # Roll: 1000, Pitch: 2000, Yaw: 3000
        data = struct.pack("<iii", 1000, 2000, 3000)
        result = decode_thingy_euler(data)

        assert result.roll == 1000
        assert result.pitch == 2000
        assert result.yaw == 3000

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x00] * 11)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_euler(data)

        assert "must be 12 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x00] * 13)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_euler(data)

        assert "must be 12 bytes" in str(exc_info.value).lower()


class TestThingyRotationMatrix:
    """Test Thingy:52 rotation matrix characteristic decoder."""

    def test_decode_valid_rotation_matrix(self) -> None:
        """Test decoding valid rotation matrix."""
        data = bytes([0x00] * 18)
        result = decode_thingy_rotation_matrix(data)

        assert isinstance(result, ThingyRotationMatrixData)
        assert result.m11 == 0
        assert result.m33 == 0

    def test_decode_non_zero_rotation_matrix(self) -> None:
        """Test decoding non-zero rotation matrix."""
        # Identity-like matrix values
        data = struct.pack("<hhhhhhhhh", 1, 0, 0, 0, 1, 0, 0, 0, 1)
        result = decode_thingy_rotation_matrix(data)

        assert result.m11 == 1
        assert result.m22 == 1
        assert result.m33 == 1
        assert result.m12 == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x00] * 17)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_rotation_matrix(data)

        assert "must be 18 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x00] * 19)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_rotation_matrix(data)

        assert "must be 18 bytes" in str(exc_info.value).lower()


class TestThingyHeading:
    """Test Thingy:52 heading characteristic decoder."""

    def test_decode_valid_heading(self) -> None:
        """Test decoding valid heading."""
        # 65536 = 1 degree in fixed-point
        data = bytes([0x00, 0x00, 0x01, 0x00])
        result = decode_thingy_heading(data)

        assert isinstance(result, ThingyHeadingData)
        assert result.heading == 65536

    def test_decode_zero_heading(self) -> None:
        """Test decoding zero heading."""
        data = bytes([0x00, 0x00, 0x00, 0x00])
        result = decode_thingy_heading(data)

        assert result.heading == 0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x00, 0x00, 0x01])

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_heading(data)

        assert "must be 4 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x00] * 5)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_heading(data)

        assert "must be 4 bytes" in str(exc_info.value).lower()


class TestThingyGravityVector:
    """Test Thingy:52 gravity vector characteristic decoder."""

    def test_decode_valid_gravity_vector(self) -> None:
        """Test decoding valid gravity vector."""
        data = bytes([0x00] * 12)
        result = decode_thingy_gravity_vector(data)

        assert isinstance(result, ThingyGravityVectorData)
        assert result.x == 0.0
        assert result.y == 0.0
        assert result.z == 0.0

    def test_decode_non_zero_gravity_vector(self) -> None:
        """Test decoding non-zero gravity vector."""
        # x: 1.0, y: 2.0, z: 9.8 m/s²
        data = struct.pack("<fff", 1.0, 2.0, 9.8)
        result = decode_thingy_gravity_vector(data)

        assert abs(result.x - 1.0) < 0.01
        assert abs(result.y - 2.0) < 0.01
        assert abs(result.z - 9.8) < 0.01

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        data = bytes([0x00] * 11)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_gravity_vector(data)

        assert "must be 12 bytes" in str(exc_info.value).lower()

    def test_decode_too_much_data(self) -> None:
        """Test error on too much data."""
        data = bytes([0x00] * 13)

        with pytest.raises(ValueError) as exc_info:
            decode_thingy_gravity_vector(data)

        assert "must be 12 bytes" in str(exc_info.value).lower()
