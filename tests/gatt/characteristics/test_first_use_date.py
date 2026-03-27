"""Tests for First Use Date characteristic (0x2C0E)."""

from __future__ import annotations

from datetime import date

import pytest

from bluetooth_sig.gatt.characteristics.first_use_date import FirstUseDateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestFirstUseDate(CommonCharacteristicTests):
    """Test suite for First Use Date characteristic."""

    @pytest.fixture
    def characteristic(self) -> FirstUseDateCharacteristic:
        return FirstUseDateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C0E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x00, 0x00, 0x00]),
                date(1970, 1, 1),
                "Epoch",
            ),
            CharacteristicTestData(
                bytearray([0x61, 0x4D, 0x00]),
                date(2024, 3, 27),
                "2024-03-27",
            ),
        ]

    def test_roundtrip(self, characteristic: FirstUseDateCharacteristic) -> None:
        d = date(2024, 1, 15)
        encoded = characteristic.build_value(d)
        result = characteristic.parse_value(encoded)
        assert result == d
