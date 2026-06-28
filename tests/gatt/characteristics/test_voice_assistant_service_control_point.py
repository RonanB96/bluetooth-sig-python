from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_service_control_point import (  # type: ignore[import-untyped]
    VoiceAssistantControlPointOpcode,
    VoiceAssistantControlPointResponseCode,
    VoiceAssistantControlPointResponseOpcode,
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
                bytearray([VoiceAssistantControlPointOpcode.START_SESSION]),
                VoiceAssistantServiceControlPointData(
                    opcode=VoiceAssistantControlPointOpcode.START_SESSION,
                ),
                "start session command",
            ),
            CharacteristicTestData(
                bytearray(
                    [
                        VoiceAssistantControlPointResponseOpcode.RESPONSE_CODE,
                        VoiceAssistantControlPointResponseCode.SUCCESS,
                    ]
                ),
                VoiceAssistantServiceControlPointData(
                    opcode=VoiceAssistantControlPointResponseOpcode.RESPONSE_CODE,
                    response_code=VoiceAssistantControlPointResponseCode.SUCCESS,
                ),
                "response code",
            ),
        ]

    def test_empty_payload_fails(self, characteristic: VoiceAssistantServiceControlPointCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_invalid_opcode_build_fails(self, characteristic: VoiceAssistantServiceControlPointCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(VoiceAssistantServiceControlPointData(opcode=300))  # type: ignore[arg-type]

    def test_command_parameters_fail(self, characteristic: VoiceAssistantServiceControlPointCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([VoiceAssistantControlPointOpcode.STOP_SESSION, 0x01]))

    def test_command_response_code_build_fails(
        self, characteristic: VoiceAssistantServiceControlPointCharacteristic
    ) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(
                VoiceAssistantServiceControlPointData(
                    opcode=VoiceAssistantControlPointOpcode.START_SESSION,
                    response_code=VoiceAssistantControlPointResponseCode.SUCCESS,
                )
            )
