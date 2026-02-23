"""Tests for LuminousEnergy characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LuminousEnergyCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLuminousEnergyCharacteristic(CommonCharacteristicTests):
    """Test suite for LuminousEnergy characteristic."""

    @pytest.fixture
    def characteristic(self) -> LuminousEnergyCharacteristic:
        """Provide LuminousEnergy characteristic."""
        return LuminousEnergyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LuminousEnergy."""
        return "2AFD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LuminousEnergy."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x00]),
                expected_value=100,
                description="100 lm*h",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00]),
                expected_value=1000,
                description="1000 lm*h",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=1,
                description="1 lm*h",
            ),
        ]
