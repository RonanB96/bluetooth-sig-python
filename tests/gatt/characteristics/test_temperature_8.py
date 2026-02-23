"""Tests for Temperature8 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Temperature8Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTemperature8Characteristic(CommonCharacteristicTests):
    """Test suite for Temperature8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> Temperature8Characteristic:
        """Provide Temperature8 characteristic."""
        return Temperature8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Temperature8."""
        return "2B0D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Temperature8."""
        return [
            CharacteristicTestData(
                input_data=bytearray([50]),
                expected_value=25.0,
                description="50 * 0.5 = 25.0 degC",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xEC]),
                expected_value=-10.0,
                description="-20 * 0.5 = -10.0 degC",
            ),
            CharacteristicTestData(
                input_data=bytearray([0]),
                expected_value=0.0,
                description="0 degC",
            ),
        ]
