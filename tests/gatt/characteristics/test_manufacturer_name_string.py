from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ManufacturerNameStringCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestManufacturerNameStringCharacteristic(CommonCharacteristicTests):
    characteristic_cls = ManufacturerNameStringCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        return ManufacturerNameStringCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A29"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(b"Apple Inc."), expected_value="Apple Inc.", description="Apple manufacturer name"
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Samsung Electronics"),
                expected_value="Samsung Electronics",
                description="Samsung manufacturer name",
            ),
            CharacteristicTestData(
                input_data=bytearray(b"Google LLC"),
                expected_value="Google LLC",
                description="Google manufacturer name",
            ),
            CharacteristicTestData(input_data=bytearray(b""), expected_value="", description="Empty manufacturer name"),
        ]
