"""Tests for Energy characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import EnergyCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestEnergyCharacteristic(CommonCharacteristicTests):
    """Test suite for Energy characteristic."""

    @pytest.fixture
    def characteristic(self) -> EnergyCharacteristic:
        """Provide Energy characteristic."""
        return EnergyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Energy."""
        return "2AF2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Energy."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x00]),
                expected_value=100,
                description="100 kWh",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=0,
                description="zero energy",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00]),
                expected_value=1000,
                description="1000 kWh",
            ),
        ]
