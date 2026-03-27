"""Tests for VolumeControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.volume_control_point import (
    VolumeControlPointCharacteristic,
    VolumeControlPointData,
    VolumeControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestVolumeControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VolumeControlPointCharacteristic:
        return VolumeControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B7E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x06, 0x05]),
                expected_value=VolumeControlPointData(
                    op_code=VolumeControlPointOpCode.MUTE,
                    change_counter=5,
                ),
                description="mute with change_counter=5",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x03, 0x80]),
                expected_value=VolumeControlPointData(
                    op_code=VolumeControlPointOpCode.SET_ABSOLUTE_VOLUME,
                    change_counter=3,
                    volume_setting=128,
                ),
                description="set absolute volume=128, change_counter=3",
            ),
        ]
