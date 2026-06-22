from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_service_control_point import (  # type: ignore[import-untyped]
    VoiceAssistantServiceControlPointCharacteristic,
    VoiceAssistantServiceControlPointData,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantServiceControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantServiceControlPointCharacteristic:
        return VoiceAssistantServiceControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C33"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x01]),
                VoiceAssistantServiceControlPointData(opcode=1, parameter=b""),
                "opcode only",
            ),
            CharacteristicTestData(
                bytearray([0x02, 0x10, 0x20]),
                VoiceAssistantServiceControlPointData(opcode=2, parameter=b"\x10\x20"),
                "opcode + params",
            ),
        ]

    def test_empty_payload_fails(self, characteristic: VoiceAssistantServiceControlPointCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_invalid_opcode_build_fails(self, characteristic: VoiceAssistantServiceControlPointCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(VoiceAssistantServiceControlPointData(opcode=300, parameter=b""))
