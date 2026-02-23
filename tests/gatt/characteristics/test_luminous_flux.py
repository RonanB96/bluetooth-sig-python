"""Tests for LuminousFlux characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LuminousFluxCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLuminousFluxCharacteristic(CommonCharacteristicTests):
    """Test suite for LuminousFlux characteristic."""

    @pytest.fixture
    def characteristic(self) -> LuminousFluxCharacteristic:
        """Provide LuminousFlux characteristic."""
        return LuminousFluxCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LuminousFlux."""
        return "2AFF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LuminousFlux."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]),
                expected_value=100,
                description="100 lm",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=1000,
                description="1000 lm",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=1,
                description="1 lm",
            ),
        ]
