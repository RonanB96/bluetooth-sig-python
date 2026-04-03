"""Tests for AnalogCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.analog import AnalogCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAnalogCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AnalogCharacteristic:
        return AnalogCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A58"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00]), 0, "Zero analog value"),
            CharacteristicTestData(bytearray([0x34, 0x12]), 0x1234, "Little-endian analog value"),
        ]
