"""Test dew point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.dew_point import DewPointCharacteristic
from bluetooth_sig.gatt.constants import SINT8_MAX, SINT8_MIN

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestDewPointCharacteristic(CommonCharacteristicTests):
    """Test Dew Point characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> DewPointCharacteristic:
        """Provide Dew Point characteristic for testing."""
        return DewPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Dew Point characteristic."""
        return "2A7B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid dew point test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([256 - 20]),  # -20°C
                expected_value=-20.0,
                description="-20°C (cold climate)",
            ),
            CharacteristicTestData(input_data=bytearray([0]), expected_value=0.0, description="0°C (freezing point)"),
            CharacteristicTestData(input_data=bytearray([10]), expected_value=10.0, description="10°C (cool)"),
            CharacteristicTestData(input_data=bytearray([25]), expected_value=25.0, description="25°C (comfortable)"),
            CharacteristicTestData(
                input_data=bytearray([SINT8_MAX]), expected_value=127.0, description="127°C (maximum)"
            ),
        ]

    def test_dew_point_parsing(self, characteristic: DewPointCharacteristic) -> None:
        """Test dew point characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "°C"

        # Test positive temperature
        data = bytearray([25])  # 25°C
        assert characteristic.parse_value(data) == 25.0

        # Test negative temperature (sint8)
        data = bytearray([256 - 10])  # -10°C
        assert characteristic.parse_value(data) == -10.0

        # Test extreme values
        data = bytearray([SINT8_MAX])  # Max positive sint8
        assert characteristic.parse_value(data) == SINT8_MAX

        # Represent the signed -128 value as its unsigned 8-bit byte (0x80)
        data = bytearray([SINT8_MIN & 0xFF])  # Max negative sint8 (SINT8_MIN)
        assert characteristic.parse_value(data) == SINT8_MIN

    def test_dew_point_boundary_values(self, characteristic: DewPointCharacteristic) -> None:
        """Test dew point boundary values."""
        # Minimum value (-128°C)
        data_min = bytearray([SINT8_MIN & 0xFF])
        assert characteristic.parse_value(data_min) == -128.0

        # Maximum value (127°C)
        data_max = bytearray([SINT8_MAX])
        assert characteristic.parse_value(data_max) == 127.0

        # Freezing point (0°C)
        data_zero = bytearray([0])
        assert characteristic.parse_value(data_zero) == 0.0

    def test_dew_point_typical_values(self, characteristic: DewPointCharacteristic) -> None:
        """Test typical dew point values."""
        # Cold climate (-20°C)
        data_cold = bytearray([256 - 20])  # Negative as unsigned byte
        assert characteristic.parse_value(data_cold) == -20.0

        # Cool (10°C)
        data_cool = bytearray([10])
        assert characteristic.parse_value(data_cool) == 10.0

        # Comfortable (25°C)
        data_comfortable = bytearray([25])
        assert characteristic.parse_value(data_comfortable) == 25.0
