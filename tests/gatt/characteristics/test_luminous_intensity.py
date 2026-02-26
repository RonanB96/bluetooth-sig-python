"""Tests for LuminousIntensity characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LuminousIntensityCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLuminousIntensityCharacteristic(CommonCharacteristicTests):
    """Test suite for LuminousIntensity characteristic."""

    @pytest.fixture
    def characteristic(self) -> LuminousIntensityCharacteristic:
        """Provide LuminousIntensity characteristic."""
        return LuminousIntensityCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LuminousIntensity."""
        return "2B01"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LuminousIntensity."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]),
                expected_value=100,
                description="100 cd",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="1000 cd",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=1,
                description="1 cd",
            ),
        ]
