"""Test heat index characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.heat_index import HeatIndexCharacteristic
from bluetooth_sig.gatt.constants import UINT8_MAX

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


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
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid heat index test data."""
        return [
            CharacteristicTestData(input_data=bytearray([27]), expected_value=27.0, description="27°C (caution level)"),
            CharacteristicTestData(
                input_data=bytearray([32]), expected_value=32.0, description="32°C (extreme caution)"
            ),
            CharacteristicTestData(input_data=bytearray([35]), expected_value=35.0, description="35°C (danger level)"),
            CharacteristicTestData(
                input_data=bytearray([41]), expected_value=41.0, description="41°C (extreme danger)"
            ),
            CharacteristicTestData(
                input_data=bytearray([UINT8_MAX]), expected_value=255.0, description="255°C (maximum)"
            ),
        ]

    def test_heat_index_parsing(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index characteristic parsing."""
        # Test normal temperature
        data = bytearray([35])  # 35°C
        assert characteristic.decode_value(data) == 35.0

        # Test max uint8
        data = bytearray([UINT8_MAX])  # UINT8_MAX°C
        assert characteristic.decode_value(data) == UINT8_MAX

    def test_heat_index_boundary_values(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index boundary values."""
        # Minimum (0°C)
        data_min = bytearray([0])
        assert characteristic.decode_value(data_min) == 0.0

        # Maximum (255°C)
        data_max = bytearray([UINT8_MAX])
        assert characteristic.decode_value(data_max) == 255.0

    def test_heat_index_danger_levels(self, characteristic: HeatIndexCharacteristic) -> None:
        """Test heat index danger levels based on typical thresholds."""
        # Caution (27°C)
        data_caution = bytearray([27])
        assert characteristic.decode_value(data_caution) == 27.0

        # Extreme caution (32°C)
        data_extreme_caution = bytearray([32])
        assert characteristic.decode_value(data_extreme_caution) == 32.0

        # Danger (41°C)
        data_danger = bytearray([41])
        assert characteristic.decode_value(data_danger) == 41.0

        # Extreme danger (54°C)
        data_extreme_danger = bytearray([54])
        assert characteristic.decode_value(data_extreme_danger) == 54.0
