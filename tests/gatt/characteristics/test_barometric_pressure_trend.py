"""Test barometric pressure trend characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BarometricPressureTrendCharacteristic
from bluetooth_sig.gatt.characteristics.barometric_pressure_trend import BarometricPressureTrend
from bluetooth_sig.gatt.constants import UINT8_MAX

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBarometricPressureTrendCharacteristic(CommonCharacteristicTests):
    """Test Barometric Pressure Trend characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BarometricPressureTrendCharacteristic:
        """Provide Barometric Pressure Trend characteristic for testing."""
        return BarometricPressureTrendCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Barometric Pressure Trend characteristic."""
        return "2AA3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid barometric pressure trend test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0]),
                expected_value=BarometricPressureTrend.UNKNOWN,
                description="Unknown trend",
            ),
            CharacteristicTestData(
                input_data=bytearray([1]),
                expected_value=BarometricPressureTrend.CONTINUOUSLY_FALLING,
                description="Continuously falling barometric pressure trend",
            ),
            CharacteristicTestData(
                input_data=bytearray([2]),
                expected_value=BarometricPressureTrend.CONTINUOUSLY_RISING,
                description="Continuously rising trend",
            ),
            CharacteristicTestData(
                input_data=bytearray([9]),
                expected_value=BarometricPressureTrend.STEADY,
                description="Steady pressure",
            ),
        ]

    def test_barometric_pressure_trend_parsing(self, characteristic: BarometricPressureTrendCharacteristic) -> None:
        """Test Barometric Pressure Trend characteristic parsing."""
        # Test metadata
        assert characteristic.unit == ""  # Enum, no units
        assert characteristic._manual_value_type == "BarometricPressureTrend"

        # Test known trend values
        test_cases = [
            (0, BarometricPressureTrend.UNKNOWN),
            (1, BarometricPressureTrend.CONTINUOUSLY_FALLING),
            (2, BarometricPressureTrend.CONTINUOUSLY_RISING),
            (9, BarometricPressureTrend.STEADY),
        ]

        for value, expected in test_cases:
            test_data = bytearray([value])
            parsed = characteristic.decode_value(test_data)
            assert parsed == expected

        # Test reserved value
        reserved_data = bytearray([UINT8_MAX])
        parsed = characteristic.decode_value(reserved_data)
        assert parsed == BarometricPressureTrend.UNKNOWN  # Falls back to UNKNOWN

    @pytest.mark.parametrize(
        "value,expected_trend",
        [
            (3, BarometricPressureTrend.FALLING_THEN_STEADY),
            (4, BarometricPressureTrend.RISING_THEN_STEADY),
            (5, BarometricPressureTrend.FALLING_BEFORE_LESSER_RISE),
            (6, BarometricPressureTrend.FALLING_BEFORE_GREATER_RISE),
            (7, BarometricPressureTrend.RISING_BEFORE_GREATER_FALL),
            (8, BarometricPressureTrend.RISING_BEFORE_LESSER_FALL),
        ],
    )
    def test_barometric_pressure_trend_all_valid_values(
        self, characteristic: BarometricPressureTrendCharacteristic, value: int, expected_trend: BarometricPressureTrend
    ) -> None:
        """Test all valid barometric pressure trend values."""
        data = bytearray([value])
        result = characteristic.decode_value(data)
        assert result == expected_trend
