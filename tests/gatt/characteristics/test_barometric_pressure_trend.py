"""Test barometric pressure trend characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BarometricPressureTrendCharacteristic
from bluetooth_sig.gatt.characteristics.barometric_pressure_trend import (
    BarometricPressureTrend,
)
from bluetooth_sig.gatt.constants import UINT8_MAX

from .test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> tuple[bytearray, BarometricPressureTrend]:
        """Valid barometric pressure trend test data."""
        return bytearray([1]), BarometricPressureTrend.CONTINUOUSLY_FALLING

    def test_barometric_pressure_trend_parsing(self, characteristic: BarometricPressureTrendCharacteristic) -> None:
        """Test Barometric Pressure Trend characteristic parsing."""
        # Test metadata
        assert characteristic.unit == ""
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
