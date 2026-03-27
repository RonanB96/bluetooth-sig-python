"""Tests for FloorNumberCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.floor_number import FloorNumberCharacteristic
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestFloorNumberCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> FloorNumberCharacteristic:
        return FloorNumberCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2AB2"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=5,
                description="Floor 5 (positive)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFE]),
                expected_value=-2,
                description="Basement level -2 (signed)",
            ),
        ]
