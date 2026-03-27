"""Tests for VolumeStateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.volume_state import (
    VolumeMuteState,
    VolumeStateCharacteristic,
    VolumeStateData,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestVolumeStateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VolumeStateCharacteristic:
        return VolumeStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B7D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x80, 0x00, 0x05]),
                expected_value=VolumeStateData(
                    volume_setting=128,
                    mute=VolumeMuteState.NOT_MUTED,
                    change_counter=5,
                ),
                description="volume=128, not muted, change_counter=5",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01, 0x0A]),
                expected_value=VolumeStateData(
                    volume_setting=0,
                    mute=VolumeMuteState.MUTED,
                    change_counter=10,
                ),
                description="volume=0, muted, change_counter=10",
            ),
        ]
