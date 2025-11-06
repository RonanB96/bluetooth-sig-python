"""Tests for Nordic Thingy:52 custom characteristic implementations."""

from __future__ import annotations

import struct

import pytest

from examples.thingy52_characteristics import (
    ThingyButtonCharacteristic,
    ThingyColorCharacteristic,
    ThingyGasCharacteristic,
    ThingyHeadingCharacteristic,
    ThingyHumidityCharacteristic,
    ThingyOrientationCharacteristic,
    ThingyPressureCharacteristic,
    ThingyTemperatureCharacteristic,
)


class TestThingyTemperatureCharacteristic:
    """Test Thingy:52 temperature characteristic."""

    def test_decode_valid_temperature(self) -> None:
        """Test decoding valid temperature value."""
        char = ThingyTemperatureCharacteristic()
        data = bytearray([0x17, 0x32])  # 23.50°C

        result = char.decode_value(data)

        assert result == 23.50

    def test_decode_negative_temperature(self) -> None:
        """Test decoding negative temperature."""
        char = ThingyTemperatureCharacteristic()
        # -5°C + 0.25 = -4.75°C (signed byte -5 = 0xFB, decimal 25 = 0x19)
        data = bytearray([0xFB, 0x19])  # -4.75°C

        result = char.decode_value(data)

        assert result == -4.75

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyTemperatureCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x17]))

        assert "must be 2 bytes" in str(exc_info.value).lower()

    def test_decode_invalid_decimal(self) -> None:
        """Test error on invalid decimal value."""
        char = ThingyTemperatureCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x17, 0x64]))  # decimal = 100

        assert "decimal must be 0-99" in str(exc_info.value).lower()


class TestThingyPressureCharacteristic:
    """Test Thingy:52 pressure characteristic."""

    def test_decode_valid_pressure(self) -> None:
        """Test decoding valid pressure value."""
        char = ThingyPressureCharacteristic()
        data = bytearray([0xE0, 0x8A, 0x01, 0x00, 0x32])  # 101088.50 Pa = 1010.8850 hPa

        result = char.decode_value(data)

        assert abs(result - 1010.8850) < 0.01

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyPressureCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0xE0, 0x8A, 0x01, 0x00]))

        assert "must be 5 bytes" in str(exc_info.value).lower()

    def test_decode_invalid_decimal(self) -> None:
        """Test error on invalid decimal value."""
        char = ThingyPressureCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0xE0, 0x8A, 0x01, 0x00, 0x64]))  # decimal = 100

        assert "decimal must be 0-99" in str(exc_info.value).lower()


class TestThingyHumidityCharacteristic:
    """Test Thingy:52 humidity characteristic."""

    def test_decode_valid_humidity(self) -> None:
        """Test decoding valid humidity value."""
        char = ThingyHumidityCharacteristic()
        data = bytearray([0x41])  # 65%

        result = char.decode_value(data)

        assert result == 65

    def test_decode_boundary_values(self) -> None:
        """Test decoding boundary humidity values."""
        char = ThingyHumidityCharacteristic()

        assert char.decode_value(bytearray([0x00])) == 0
        assert char.decode_value(bytearray([0x64])) == 100

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyHumidityCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([]))

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_out_of_range(self) -> None:
        """Test error on out-of-range value."""
        char = ThingyHumidityCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x65]))  # 101%

        assert "must be 0-100" in str(exc_info.value).lower()


class TestThingyGasCharacteristic:
    """Test Thingy:52 gas characteristic."""

    def test_decode_valid_gas(self) -> None:
        """Test decoding valid gas sensor values."""
        char = ThingyGasCharacteristic()
        data = bytearray([0x90, 0x01, 0x32, 0x00])  # eCO2: 400 ppm, TVOC: 50 ppb

        result = char.decode_value(data)

        assert result["eco2_ppm"] == 400
        assert result["tvoc_ppb"] == 50

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyGasCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x90, 0x01, 0x32]))

        assert "must be 4 bytes" in str(exc_info.value).lower()

    def test_encode_gas_data(self) -> None:
        """Test encoding gas data."""
        char = ThingyGasCharacteristic()
        data = {"eco2_ppm": 400, "tvoc_ppb": 50}

        result = char.encode_value(data)

        assert result == bytearray([0x90, 0x01, 0x32, 0x00])


class TestThingyColorCharacteristic:
    """Test Thingy:52 color characteristic."""

    def test_decode_valid_color(self) -> None:
        """Test decoding valid color values."""
        char = ThingyColorCharacteristic()
        data = bytearray([0xFF, 0x00, 0x80, 0x00, 0x40, 0x00, 0x00, 0x01])

        result = char.decode_value(data)

        assert result["red"] == 255
        assert result["green"] == 128
        assert result["blue"] == 64
        assert result["clear"] == 256

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyColorCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0xFF] * 7))

        assert "must be 8 bytes" in str(exc_info.value).lower()


class TestThingyButtonCharacteristic:
    """Test Thingy:52 button characteristic."""

    def test_decode_button_pressed(self) -> None:
        """Test decoding button pressed state."""
        char = ThingyButtonCharacteristic()
        data = bytearray([0x01])

        result = char.decode_value(data)

        assert result is True

    def test_decode_button_released(self) -> None:
        """Test decoding button released state."""
        char = ThingyButtonCharacteristic()
        data = bytearray([0x00])

        result = char.decode_value(data)

        assert result is False

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyButtonCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([]))

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_invalid_state(self) -> None:
        """Test error on invalid button state."""
        char = ThingyButtonCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x02]))

        assert "must be 0 or 1" in str(exc_info.value).lower()


class TestThingyOrientationCharacteristic:
    """Test Thingy:52 orientation characteristic."""

    def test_decode_valid_orientations(self) -> None:
        """Test decoding valid orientation values."""
        char = ThingyOrientationCharacteristic()

        assert char.decode_value(bytearray([0x00])) == "Portrait"
        assert char.decode_value(bytearray([0x01])) == "Landscape"
        assert char.decode_value(bytearray([0x02])) == "Reverse Portrait"

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyOrientationCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([]))

        assert "must be 1 byte" in str(exc_info.value).lower()

    def test_decode_invalid_orientation(self) -> None:
        """Test error on invalid orientation value."""
        char = ThingyOrientationCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x03]))

        assert "must be 0-2" in str(exc_info.value).lower()


class TestThingyHeadingCharacteristic:
    """Test Thingy:52 heading characteristic."""

    def test_decode_valid_heading(self) -> None:
        """Test decoding valid heading."""
        char = ThingyHeadingCharacteristic()
        # 90 degrees = 90 * 65536 = 5898240
        data = bytearray(struct.pack("<i", 5898240))

        result = char.decode_value(data)

        assert abs(result - 90.0) < 0.01

    def test_decode_zero_heading(self) -> None:
        """Test decoding zero heading."""
        char = ThingyHeadingCharacteristic()
        data = bytearray([0x00, 0x00, 0x00, 0x00])

        result = char.decode_value(data)

        assert result == 0.0

    def test_decode_insufficient_data(self) -> None:
        """Test error on insufficient data."""
        char = ThingyHeadingCharacteristic()

        with pytest.raises(ValueError) as exc_info:
            char.decode_value(bytearray([0x00, 0x00, 0x01]))

        assert "must be 4 bytes" in str(exc_info.value).lower()
