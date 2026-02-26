"""Tests for TimeSecond32 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeSecond32Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeSecond32Characteristic(CommonCharacteristicTests):
    """Test suite for TimeSecond32 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeSecond32Characteristic:
        """Provide TimeSecond32 characteristic."""
        return TimeSecond32Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeSecond32."""
        return "2BE6"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeSecond32."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x0E, 0x00, 0x00]),
                expected_value=datetime.timedelta(seconds=3600),
                description="3600 seconds",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=datetime.timedelta(seconds=1),
                description="1 second",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x51, 0x01, 0x00]),
                expected_value=datetime.timedelta(seconds=86400),
                description="86400 sec = 1 day",
            ),
        ]
