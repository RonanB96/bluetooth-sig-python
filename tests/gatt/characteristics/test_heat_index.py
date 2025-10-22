"""Test heat index characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.heat_index import HeatIndexCharacteristic
from bluetooth_sig.gatt.constants import UINT8_MAX

from .test_characteristic_common import CommonCharacteristicTests


class TestHeatIndexCharacteristic(CommonCharacteristicTests):
    """Test Heat Index characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> HeatIndexCharacteristic:
        """Provide Heat Index characteristic for testing."""
        return HeatIndexCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Heat Index characteristic."""
        return "2A7A"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid heat index test data."""
        return bytearray([35]), 35.0  # 35°C

    def test_heat_index_parsing(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index characteristic parsing."""
        # Test normal temperature
        data = bytearray([35])  # 35°C
        assert characteristic.decode_value(data) == 35.0

        # Test max uint8
        data = bytearray([UINT8_MAX])  # UINT8_MAX°C
        assert characteristic.decode_value(data) == UINT8_MAX
