"""Tests for Temperature characteristic (0x2A6E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.temperature import TemperatureCharacteristic
from bluetooth_sig.gatt.constants import SINT16_MAX
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTemperatureCharacteristic(CommonCharacteristicTests):
    """Test Temperature characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        """Provide Temperature characteristic for testing."""
        return TemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Temperature characteristic."""
        return "2A6E"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid temperature test data covering various temperatures and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]), expected_value=0.0, description="0°C (freezing point)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x08]), expected_value=21.48, description="21.48°C (room temperature)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x18, 0xFC]), expected_value=-10.0, description="-10°C (cold temperature)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x7F]), expected_value=327.67, description="327.67°C (maximum temperature)"
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]), expected_value=0.01, description="0.01°C (precision test)"
            ),
        ]

    # === Temperature-Specific Tests ===
    def test_temperature_precision_and_boundaries(self, characteristic: BaseCharacteristic) -> None:
        """Test temperature precision and boundary values."""
        # Test freezing point (0°C)
        result = characteristic.parse_value(bytearray([0x00, 0x00]))
        assert result.parse_success
        assert result.value == 0.0

        # Test negative temperature (-10°C)
        result = characteristic.parse_value(bytearray([0x18, 0xFC]))  # -1000 = -10.00°C
        assert result.parse_success
        assert result.value is not None
        assert abs(result.value + 10.0) < 0.01

        # Test precision (21.48°C)
        result = characteristic.parse_value(bytearray([0x64, 0x08]))  # 2148 = 21.48°C
        assert result.parse_success
        assert result.value is not None
        assert abs(result.value - 21.48) < 0.01

    def test_temperature_extreme_values(self, characteristic: BaseCharacteristic) -> None:
        """Test extreme temperature values within valid range."""
        # Test maximum positive value
        max_data = bytearray([SINT16_MAX & 0xFF, (SINT16_MAX >> 8) & 0xFF])  # 32767 = 327.67°C
        result = characteristic.parse_value(max_data)
        assert result.parse_success
        assert result.value is not None
        assert abs(result.value - 327.67) < 0.01

        # Test minimum valid temperature (-273.15°C, which is -27315 as signed int16)
        # -27315 in little-endian = 0x4D, 0x95
        min_data = bytearray([0x4D, 0x95])  # -27315 = -273.15°C (absolute zero)
        result = characteristic.parse_value(min_data)
        assert result.parse_success
        assert result.value is not None
        temp_value: float = result.value  # Type assertion for mypy
        assert abs(temp_value + 273.15) < 0.01
