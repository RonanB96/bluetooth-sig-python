"""Tests for IMD Historical Data characteristic (0x2C13)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.imd_historical_data import IMDHistoricalDataCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIMDHistoricalDataCharacteristic(CommonCharacteristicTests):
    """Test suite for IMD Historical Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> IMDHistoricalDataCharacteristic:
        return IMDHistoricalDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C13"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x55]),
                expected_value=b"\x55",
                description="Single byte historical record",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6]),
                expected_value=b"\xa1\xb2\xc3\xd4\xe5\xf6",
                description="Multi-byte historical record",
            ),
        ]
