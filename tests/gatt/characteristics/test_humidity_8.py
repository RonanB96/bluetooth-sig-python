"""Tests for Humidity8 characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Humidity8Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHumidity8Characteristic(CommonCharacteristicTests):
    """Test suite for Humidity8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> Humidity8Characteristic:
        """Provide Humidity8 characteristic."""
        return Humidity8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Humidity8."""
        return "2C1B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for Humidity8."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0]),
                expected_value=0.0,
                description="0%",
            ),
            CharacteristicTestData(
                input_data=bytearray([100]),
                expected_value=50.0,
                description="100 * 0.5 = 50%",
            ),
            CharacteristicTestData(
                input_data=bytearray([200]),
                expected_value=100.0,
                description="200 * 0.5 = 100%",
            ),
        ]
