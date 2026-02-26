"""Tests for DateUtc characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import DateUtcCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestDateUtcCharacteristic(CommonCharacteristicTests):
    """Test suite for DateUtc characteristic."""

    @pytest.fixture
    def characteristic(self) -> DateUtcCharacteristic:
        """Provide DateUtc characteristic."""
        return DateUtcCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for DateUtc."""
        return "2AED"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for DateUtc."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00]),
                expected_value=datetime.date(1970, 1, 2),
                description="day 1 = 1970-01-02",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xEB, 0x4D, 0x00]),
                expected_value=datetime.date(2024, 8, 12),
                description="day 19723",
            ),
        ]
