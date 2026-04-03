"""Tests for AudioInputControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_input_control_point import (
    AudioInputControlPointCharacteristic,
    AudioInputControlPointData,
    AudioInputControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioInputControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AudioInputControlPointCharacteristic:
        return AudioInputControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B7B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x0A, 0x15]),
                expected_value=AudioInputControlPointData(
                    op_code=AudioInputControlPointOpCode.SET_GAIN_SETTING,
                    change_counter=10,
                    gain_setting=21,
                ),
                description="SET_GAIN_SETTING with gain=21, counter=10",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x05]),
                expected_value=AudioInputControlPointData(
                    op_code=AudioInputControlPointOpCode.UNMUTE,
                    change_counter=5,
                    gain_setting=None,
                ),
                description="UNMUTE with counter=5, no gain setting",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0xF0]),
                expected_value=AudioInputControlPointData(
                    op_code=AudioInputControlPointOpCode.SET_GAIN_SETTING,
                    change_counter=0,
                    gain_setting=-16,
                ),
                description="SET_GAIN_SETTING with negative gain (-16)",
            ),
        ]
