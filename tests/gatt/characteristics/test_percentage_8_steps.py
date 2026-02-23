"""Tests for Percentage8Steps characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Percentage8StepsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestPercentage8StepsCharacteristic(CommonCharacteristicTests):
    """Test suite for Percentage8Steps characteristic."""

    @pytest.fixture
    def characteristic(self) -> Percentage8StepsCharacteristic:
        """Provide Percentage8Steps characteristic."""
        return Percentage8StepsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Percentage8Steps."""
        return "2C05"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Percentage8Steps."""
        return [
            CharacteristicTestData(
                input_data=bytearray([1]),
                expected_value=1,
                description="1% (minimum valid)",
            ),
            CharacteristicTestData(
                input_data=bytearray([50]),
                expected_value=50,
                description="50%",
            ),
            CharacteristicTestData(
                input_data=bytearray([200]),
                expected_value=200,
                description="200 (maximum valid)",
            ),
        ]
