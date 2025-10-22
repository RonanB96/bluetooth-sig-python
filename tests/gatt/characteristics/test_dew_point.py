"""Test dew point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.dew_point import DewPointCharacteristic
from bluetooth_sig.gatt.constants import SINT8_MAX, SINT8_MIN

from .test_characteristic_common import CommonCharacteristicTests


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
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid dew point test data."""
        return bytearray([25]), 25.0  # 25°C

    def test_dew_point_parsing(self, characteristic: DewPointCharacteristic) -> None:
        """Test dew point characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "°C"

        # Test positive temperature
        data = bytearray([25])  # 25°C
        assert characteristic.decode_value(data) == 25.0

        # Test negative temperature (sint8)
        data = bytearray([256 - 10])  # -10°C
        assert characteristic.decode_value(data) == -10.0

        # Test extreme values
        data = bytearray([SINT8_MAX])  # Max positive sint8
        assert characteristic.decode_value(data) == SINT8_MAX

        # Represent the signed -128 value as its unsigned 8-bit byte (0x80)
        data = bytearray([SINT8_MIN & 0xFF])  # Max negative sint8 (SINT8_MIN)
        assert characteristic.decode_value(data) == SINT8_MIN
