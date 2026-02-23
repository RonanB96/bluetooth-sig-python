"""Tests for EstimatedServiceDate characteristic."""

from __future__ import annotations

import datetime

import pytest

from bluetooth_sig.gatt.characteristics import EstimatedServiceDateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestEstimatedServiceDateCharacteristic(CommonCharacteristicTests):
    """Test suite for EstimatedServiceDate characteristic."""

    @pytest.fixture
    def characteristic(self) -> EstimatedServiceDateCharacteristic:
        """Provide EstimatedServiceDate characteristic."""
        return EstimatedServiceDateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for EstimatedServiceDate."""
        return "2BEF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for EstimatedServiceDate."""
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
