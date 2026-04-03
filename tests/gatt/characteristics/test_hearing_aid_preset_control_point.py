"""Tests for HearingAidPresetControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.hearing_aid_preset_control_point import (
    HearingAidPresetControlPointCharacteristic,
    HearingAidPresetControlPointData,
    HearingAidPresetControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestHearingAidPresetControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> HearingAidPresetControlPointCharacteristic:
        return HearingAidPresetControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BDB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=HearingAidPresetControlPointData(
                    opcode=HearingAidPresetControlPointOpCode.SET_ACTIVE_PRESET,
                    parameter=b"",
                ),
                description="Set active preset, no parameter",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x01, 0x4D, 0x79, 0x50]),
                expected_value=HearingAidPresetControlPointData(
                    opcode=HearingAidPresetControlPointOpCode.WRITE_PRESET_NAME,
                    parameter=b"\x01MyP",
                ),
                description="Write preset name with parameter bytes",
            ),
        ]
