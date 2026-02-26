"""Tests for TimeSecond16 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeSecond16Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeSecond16Characteristic(CommonCharacteristicTests):
    """Test suite for TimeSecond16 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeSecond16Characteristic:
        """Provide TimeSecond16 characteristic."""
        return TimeSecond16Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeSecond16."""
        return "2B16"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeSecond16."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x3C, 0x00]),
                expected_value=datetime.timedelta(seconds=60),
                description="60 seconds",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=datetime.timedelta(seconds=1),
                description="1 second",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x0E]),
                expected_value=datetime.timedelta(seconds=3600),
                description="3600 seconds",
            ),
        ]
