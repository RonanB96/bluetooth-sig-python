"""Tests for HighTemperature characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import HighTemperatureCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHighTemperatureCharacteristic(CommonCharacteristicTests):
    """Test suite for HighTemperature characteristic."""

    @pytest.fixture
    def characteristic(self) -> HighTemperatureCharacteristic:
        """Provide HighTemperature characteristic."""
        return HighTemperatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for HighTemperature."""
        return "2BDF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for HighTemperature."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=500.0,
                description="1000 * 0.5 = 500.0 degC",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=0.5,
                description="1 * 0.5 = 0.5 degC",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF]),
                expected_value=-0.5,
                description="-1 * 0.5 = -0.5 degC",
            ),
        ]
