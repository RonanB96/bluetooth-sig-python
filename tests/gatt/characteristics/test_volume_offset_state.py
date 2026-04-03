"""Tests for VolumeOffsetStateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.volume_offset_state import (
    VolumeOffsetStateCharacteristic,
    VolumeOffsetStateData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestVolumeOffsetStateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VolumeOffsetStateCharacteristic:
        return VolumeOffsetStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B80"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x05]),
                expected_value=VolumeOffsetStateData(
                    volume_offset=100,
                    change_counter=5,
                ),
                description="offset=100, change_counter=5",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xCE, 0xFF, 0x0A]),
                expected_value=VolumeOffsetStateData(
                    volume_offset=-50,
                    change_counter=10,
                ),
                description="offset=-50, change_counter=10",
            ),
        ]
