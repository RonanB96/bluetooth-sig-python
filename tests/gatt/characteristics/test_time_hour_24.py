"""Tests for TimeHour24 characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import TimeHour24Characteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestTimeHour24Characteristic(CommonCharacteristicTests):
    """Test suite for TimeHour24 characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeHour24Characteristic:
        """Provide TimeHour24 characteristic."""
        return TimeHour24Characteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for TimeHour24."""
        return "2B14"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for TimeHour24."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=datetime.timedelta(hours=1),
                description="1 hour",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x18, 0x00, 0x00]),
                expected_value=datetime.timedelta(hours=24),
                description="24 hours",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x00, 0x00]),
                expected_value=datetime.timedelta(hours=2),
                description="2 hours",
            ),
        ]
