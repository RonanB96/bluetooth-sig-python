"""Test pollen concentration characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import PollenConcentrationCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPollenConcentrationCharacteristic(CommonCharacteristicTests):
    """Test Pollen Concentration characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Pollen Concentration characteristic for testing."""
        return PollenConcentrationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Pollen Concentration characteristic."""
        return "2A75"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid pollen concentration test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=0.0,
                description="Zero pollen concentration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=1.0,
                description="Minimum pollen concentration (1 grain/m³)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x40, 0xE2, 0x01]),
                expected_value=123456.0,
                description="123456.0 grains/m³ pollen concentration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF]),
                expected_value=16777215.0,
                description="Maximum pollen concentration",
            ),
        ]

    def test_pollen_concentration_parsing(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test Pollen Concentration characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "grains/m³"

        # Test normal parsing: 123456 count/m³
        test_data = bytearray([0x40, 0xE2, 0x01])  # 123456 in 24-bit little endian
        parsed = characteristic.parse_value(test_data)
        assert parsed.value == 123456.0  # Returns float now
