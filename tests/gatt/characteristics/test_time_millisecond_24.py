"""Tests for TimeMillisecond24 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeMillisecond24Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeMillisecond24Characteristic(CommonCharacteristicTests):
    """Test suite for TimeMillisecond24 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeMillisecond24Characteristic:
        """Provide TimeMillisecond24 characteristic."""
        return TimeMillisecond24Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeMillisecond24."""
        return "2B15"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeMillisecond24."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00]),
                expected_value=datetime.timedelta(seconds=1),
                description="1000 ms = 1 sec",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=datetime.timedelta(milliseconds=1),
                description="1 ms",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xD0, 0x07, 0x00]),
                expected_value=datetime.timedelta(seconds=2),
                description="2000 ms = 2 sec",
            ),
        ]
