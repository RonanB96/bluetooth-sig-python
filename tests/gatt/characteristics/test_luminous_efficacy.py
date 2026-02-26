"""Tests for LuminousEfficacy characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import LuminousEfficacyCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestLuminousEfficacyCharacteristic(CommonCharacteristicTests):
    """Test suite for LuminousEfficacy characteristic."""

    @pytest.fixture
    def characteristic(self) -> LuminousEfficacyCharacteristic:
        """Provide LuminousEfficacy characteristic."""
        return LuminousEfficacyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for LuminousEfficacy."""
        return "2AFC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for LuminousEfficacy."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00]),
                expected_value=10.0,
                description="100 * 0.1 = 10.0 lm/W",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]),
                expected_value=100.0,
                description="1000 * 0.1 = 100.0 lm/W",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=0.1,
                description="1 * 0.1 = 0.1 lm/W",
            ),
        ]
