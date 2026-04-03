"""Tests for VolumeOffsetControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.volume_offset_control_point import (
    VolumeOffsetControlPointCharacteristic,
    VolumeOffsetControlPointData,
    VolumeOffsetControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestVolumeOffsetControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VolumeOffsetControlPointCharacteristic:
        return VolumeOffsetControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B82"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x0A, 0x32, 0x00]),
                expected_value=VolumeOffsetControlPointData(
                    op_code=VolumeOffsetControlPointOpCode.SET_VOLUME_OFFSET,
                    change_counter=10,
                    volume_offset=50,
                ),
                description="set volume offset=50, change_counter=10",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x05, 0x9C, 0xFF]),
                expected_value=VolumeOffsetControlPointData(
                    op_code=VolumeOffsetControlPointOpCode.SET_VOLUME_OFFSET,
                    change_counter=5,
                    volume_offset=-100,
                ),
                description="set volume offset=-100, change_counter=5",
            ),
        ]
