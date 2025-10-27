from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import UVIndexCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.uv_index import UVIndexCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestUVIndexCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return UVIndexCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A76"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        # Example: UV Index = 7 (high)
        return CharacteristicTestData(input_data=bytearray([7]), expected_value=7, description="UV Index = 7 (high)")
