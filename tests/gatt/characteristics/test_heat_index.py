"""Test heat index characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.heat_index import HeatIndexCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHeatIndexCharacteristic(CommonCharacteristicTests):
    """Test Heat Index characteristic implementation.

    GSS: sint8, unit °C, M=1 d=0 b=0 (no scaling).
    """

    @pytest.fixture
    def characteristic(self) -> HeatIndexCharacteristic:
        """Provide Heat Index characteristic for testing."""
        return HeatIndexCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Heat Index characteristic."""
        return "2A7A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid heat index test data (sint8)."""
        return [
            CharacteristicTestData(input_data=bytearray([27]), expected_value=27, description="27°C (caution level)"),
            CharacteristicTestData(input_data=bytearray([35]), expected_value=35, description="35°C (danger level)"),
            CharacteristicTestData(
                input_data=bytearray([0xE5]), expected_value=-27, description="-27°C (negative, sint8)"
            ),
        ]

    def test_heat_index_parsing(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index characteristic parsing."""
        assert characteristic.parse_value(bytearray([35])) == 35
        assert characteristic.parse_value(bytearray([0])) == 0

    def test_heat_index_negative_values(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index negative values (sint8 range -128..127)."""
        assert characteristic.parse_value(bytearray([0xFF])) == -1
        assert characteristic.parse_value(bytearray([0x80])) == -128
        assert characteristic.parse_value(bytearray([0x7F])) == 127

    def test_heat_index_danger_levels(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index danger levels based on typical thresholds."""
        assert characteristic.parse_value(bytearray([27])) == 27
        assert characteristic.parse_value(bytearray([32])) == 32
        assert characteristic.parse_value(bytearray([41])) == 41
        assert characteristic.parse_value(bytearray([54])) == 54
