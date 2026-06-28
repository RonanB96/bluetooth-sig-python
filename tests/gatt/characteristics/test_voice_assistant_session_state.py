from __future__ import annotations

from typing import cast

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_session_state import (  # type: ignore[import-untyped]
    VoiceAssistantSessionState,
    VoiceAssistantSessionStateCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantSessionStateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantSessionStateCharacteristic:
        return VoiceAssistantSessionStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C35"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([VoiceAssistantSessionState.SESSION_RESET]),
                VoiceAssistantSessionState.SESSION_RESET,
                "reset",
            ),
            CharacteristicTestData(
                bytearray([VoiceAssistantSessionState.SESSION_ACTIVE]),
                VoiceAssistantSessionState.SESSION_ACTIVE,
                "active",
            ),
        ]

    def test_empty_payload_fails(self, characteristic: VoiceAssistantSessionStateCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_build_out_of_range_fails(self, characteristic: VoiceAssistantSessionStateCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(cast(VoiceAssistantSessionState, 999))
