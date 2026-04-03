"""Tests for BearerUCICharacteristic (2BB4)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_uci import BearerUCICharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerUCI(CommonCharacteristicTests):
    """Test suite for BearerUCICharacteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerUCICharacteristic:
        return BearerUCICharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB4"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"skype"), "skype", "Skype UCI"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
