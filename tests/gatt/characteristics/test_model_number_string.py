from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import ModelNumberStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestModelNumberStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = ModelNumberStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return ModelNumberStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A24"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"iPhone 15 Pro"),
                expected_value="iPhone 15 Pro",
                description="iPhone model number",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Galaxy S23"),
                expected_value="Galaxy S23",
                description="Samsung model number",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Pixel 8"),
                expected_value="Pixel 8",
                description="Google model number",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty model number"),
        ]
