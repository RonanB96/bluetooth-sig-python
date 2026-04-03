"""Tests for HidControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.hid_control_point import (
    HidControlPointCharacteristic,
    HidControlPointCommand,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHidControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> HidControlPointCharacteristic:
        return HidControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A4C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=HidControlPointCommand.SUSPEND,
                description="Suspend command",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=HidControlPointCommand.EXIT_SUSPEND,
                description="Exit suspend command",
            ),
        ]
