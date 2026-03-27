"""Tests for AudioInputStateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_input_state import (
    AudioInputGainMode,
    AudioInputMuteState,
    AudioInputStateCharacteristic,
    AudioInputStateData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioInputStateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AudioInputStateCharacteristic:
        return AudioInputStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B77"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=AudioInputStateData(
                    gain_setting=0,
                    mute=AudioInputMuteState.NOT_MUTED,
                    gain_mode=AudioInputGainMode.MANUAL_ONLY,
                    change_counter=0,
                ),
                description="All zeros: gain=0, not muted, manual, counter=0",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xEC, 0x01, 0x02, 0xFF]),
                expected_value=AudioInputStateData(
                    gain_setting=-20,
                    mute=AudioInputMuteState.MUTED,
                    gain_mode=AudioInputGainMode.MANUAL_AUTOMATIC,
                    change_counter=255,
                ),
                description="gain=-20, muted, manual+auto mode, counter=255",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x32, 0x02, 0x01, 0x0A]),
                expected_value=AudioInputStateData(
                    gain_setting=50,
                    mute=AudioInputMuteState.DISABLED,
                    gain_mode=AudioInputGainMode.AUTOMATIC_ONLY,
                    change_counter=10,
                ),
                description="gain=50, mute disabled, automatic mode, counter=10",
            ),
        ]
