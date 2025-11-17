"""Tests for Nordic Thingy:52 vendor characteristics."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.exceptions import InsufficientDataError, ValueRangeError
from examples.thingy52.thingy52_characteristics import (
    ThingyButtonCharacteristic,
    ThingyColorCharacteristic,
    ThingyGasCharacteristic,
    ThingyHeadingCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyOrientationCharacteristic,
    ThingyPressureCharacteristic,
    ThingyTemperatureCharacteristic,
)


@pytest.fixture(autouse=True, scope="session")
def auto_register_thingy_characteristics() -> None:
    """Auto-register Thingy:52 characteristics via CustomBaseCharacteristic."""
    # CustomBaseCharacteristic handles auto-registration on first instantiation
    # Just instantiate one of each to trigger registration
    ThingyTemperatureCharacteristic()
    ThingyPressureCharacteristic()
    ThingyHumidityCharacteristic()
    ThingyGasCharacteristic()
    ThingyColorCharacteristic()
    ThingyButtonCharacteristic()
    ThingyOrientationCharacteristic()
    ThingyHeadingCharacteristic()


class TestThingyTemperatureCharacteristic:
    """Test Thingy:52 temperature characteristic."""

    def test_decode_valid_temperature(self) -> None:
        """Test decoding valid temperature data."""
        char = ThingyTemperatureCharacteristic()
        # 25.5°C: integer=25, decimal=128 (128/256=0.5)
        data = bytearray([25, 128])
        result = char.decode_value(data)
        assert result.temperature_celsius == 25.5

    def test_decode_negative_temperature(self) -> None:
        """Test decoding negative temperature data."""
        char = ThingyTemperatureCharacteristic()
        # -5.25°C: integer=-5, decimal=64 (64/256=0.25)
        data = bytearray([251, 64])  # 251 = -5 as signed int8
        result = char.decode_value(data)
        assert result.temperature_celsius == -4.75

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyTemperatureCharacteristic()
        data = bytearray([25])  # Only 1 byte
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyPressureCharacteristic:
    """Test Thingy:52 pressure characteristic."""

    def test_decode_valid_pressure(self) -> None:
        """Test decoding valid pressure data."""
        char = ThingyPressureCharacteristic()
        # 1013.25 hPa: integer=1013, decimal=64 (64/256=0.25)
        data = bytearray([245, 3, 0, 0, 64])  # 1013 = 0x000003F5 LE
        result = char.decode_value(data)
        assert result.pressure_hpa == 1013.25

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyPressureCharacteristic()
        data = bytearray([245, 3, 0, 0])  # Only 4 bytes
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyHumidityCharacteristic:
    """Test Thingy:52 humidity characteristic."""

    def test_decode_valid_humidity(self) -> None:
        """Test decoding valid humidity data."""
        char = ThingyHumidityCharacteristic()
        data = bytearray([65])  # 65%
        result = char.decode_value(data)
        assert result.humidity_percent == 65

    def test_decode_humidity_too_low(self) -> None:
        """Test decoding humidity below minimum."""
        char = ThingyHumidityCharacteristic()
        data = bytearray([255])  # -1%
        with pytest.raises(ValueRangeError):
            char.decode_value(data)

    def test_decode_humidity_too_high(self) -> None:
        """Test decoding humidity above maximum."""
        char = ThingyHumidityCharacteristic()
        data = bytearray([101])  # 101%
        with pytest.raises(ValueRangeError):
            char.decode_value(data)

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyHumidityCharacteristic()
        data = bytearray([])  # Empty
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyGasCharacteristic:
    """Test Thingy:52 gas characteristic."""

    def test_decode_valid_gas(self) -> None:
        """Test decoding valid gas data."""
        char = ThingyGasCharacteristic()
        # eCO2: 400 ppm, TVOC: 0 ppb
        data = bytearray([144, 1, 0, 0])  # 400 = 0x0190 LE, 0 = 0x0000 LE
        result = char.decode_value(data)
        assert result.eco2_ppm == 400
        assert result.tvoc_ppb == 0

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyGasCharacteristic()
        data = bytearray([144, 1, 0])  # Only 3 bytes
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyColorCharacteristic:
    """Test Thingy:52 color characteristic."""

    def test_decode_valid_color(self) -> None:
        """Test decoding valid color data."""
        char = ThingyColorCharacteristic()
        # Red: 255, Green: 128, Blue: 64, Clear: 512
        data = bytearray([255, 0, 128, 0, 64, 0, 0, 2])  # All LE uint16
        result = char.decode_value(data)
        assert result.red == 255
        assert result.green == 128
        assert result.blue == 64
        assert result.clear == 512

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyColorCharacteristic()
        data = bytearray([255, 0, 128, 0, 64, 0, 0])  # Only 7 bytes
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyButtonCharacteristic:
    """Test Thingy:52 button characteristic."""

    def test_decode_button_pressed(self) -> None:
        """Test decoding button pressed state."""
        char = ThingyButtonCharacteristic()
        data = bytearray([0])  # 0 = pressed
        result = char.decode_value(data)
        assert result.pressed is True

    def test_decode_button_released(self) -> None:
        """Test decoding button released state."""
        char = ThingyButtonCharacteristic()
        data = bytearray([1])  # 1 = released
        result = char.decode_value(data)
        assert result.pressed is False

    def test_decode_invalid_button_state(self) -> None:
        """Test decoding invalid button state."""
        char = ThingyButtonCharacteristic()
        data = bytearray([2])  # Invalid state
        with pytest.raises(ValueRangeError):
            char.decode_value(data)

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyButtonCharacteristic()
        data = bytearray([])  # Empty
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyOrientationCharacteristic:
    """Test Thingy:52 orientation characteristic."""

    def test_decode_valid_orientation(self) -> None:
        """Test decoding valid orientation data."""
        char = ThingyOrientationCharacteristic()
        data = bytearray([1])  # Orientation value 1
        result = char.decode_value(data)
        assert result.orientation == 1

    def test_decode_orientation_too_low(self) -> None:
        """Test decoding orientation below minimum."""
        char = ThingyOrientationCharacteristic()
        data = bytearray([255])  # -1
        with pytest.raises(ValueRangeError):
            char.decode_value(data)

    def test_decode_orientation_too_high(self) -> None:
        """Test decoding orientation above maximum."""
        char = ThingyOrientationCharacteristic()
        data = bytearray([3])  # 3 > 2
        with pytest.raises(ValueRangeError):
            char.decode_value(data)

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyOrientationCharacteristic()
        data = bytearray([])  # Empty
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)


class TestThingyHeadingCharacteristic:
    """Test Thingy:52 heading characteristic."""

    def test_decode_valid_heading(self) -> None:
        """Test decoding valid heading data."""
        char = ThingyHeadingCharacteristic()
        # 90.0 degrees as float32 LE
        data = bytearray([0x00, 0x00, 0xB4, 0x42])  # 90.0f in IEEE 754
        result = char.decode_value(data)
        assert abs(result.heading_degrees - 90.0) < 0.01

    def test_decode_insufficient_data(self) -> None:
        """Test decoding with insufficient data."""
        char = ThingyHeadingCharacteristic()
        data = bytearray([0x00, 0x00, 0x5A])  # Only 3 bytes
        with pytest.raises(InsufficientDataError):
            char.decode_value(data)
