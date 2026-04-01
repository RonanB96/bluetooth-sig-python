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
        """Valid FloorNumber test data.

        IPS spec §3.6: raw uint8 X = N + 20; decoded floor N = X − 20.
        """
        return [
            # X=25: N = 25−20 = 5  (floor 5)
            CharacteristicTestData(
                input_data=bytearray([0x19]),
                expected_value=5,
                description="Floor 5",
            ),
            # X=18: N = 18−20 = −2  (basement level −2)
            CharacteristicTestData(
                input_data=bytearray([0x12]),
                expected_value=-2,
                description="Basement level -2",
            ),
        ]
