"""Tests for TimeSecond8 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeSecond8Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeSecond8Characteristic(CommonCharacteristicTests):
    """Test suite for TimeSecond8 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeSecond8Characteristic:
        """Provide TimeSecond8 characteristic."""
        return TimeSecond8Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeSecond8."""
        return "2B17"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeSecond8."""
        return [
            CharacteristicTestData(
                input_data=bytearray([10]),
                expected_value=datetime.timedelta(seconds=10),
                description="10 seconds",
            ),
            CharacteristicTestData(
                input_data=bytearray([1]),
                expected_value=datetime.timedelta(seconds=1),
                description="1 second",
            ),
            CharacteristicTestData(
                input_data=bytearray([60]),
                expected_value=datetime.timedelta(seconds=60),
                description="60 seconds",
            ),
        ]
