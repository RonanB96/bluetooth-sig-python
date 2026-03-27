"""Tests for ESLCurrentAbsoluteTimeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.esl_current_absolute_time import (
    ESLCurrentAbsoluteTimeCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestESLCurrentAbsoluteTimeCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ESLCurrentAbsoluteTimeCharacteristic:
        return ESLCurrentAbsoluteTimeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BF9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero milliseconds (epoch start)",
            ),
            CharacteristicTestData(
                # 0x000F4240 = 1000000 ms = 1000 seconds, LE: 0x40, 0x42, 0x0F, 0x00
                input_data=bytearray([0x40, 0x42, 0x0F, 0x00]),
                expected_value=1_000_000,
                description="1,000,000 milliseconds (1000 seconds)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=0xFFFFFFFF,
                description="Maximum uint32 value",
            ),
        ]
