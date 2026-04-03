"""Tests for CoordinatedSetNameCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.coordinated_set_name import CoordinatedSetNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCoordinatedSetNameCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CoordinatedSetNameCharacteristic:
        return CoordinatedSetNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C1A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Set A"), "Set A", "Basic UTF-8 set name"),
            CharacteristicTestData(bytearray(b"Kitchen Cluster"), "Kitchen Cluster", "Longer UTF-8 set name"),
        ]
