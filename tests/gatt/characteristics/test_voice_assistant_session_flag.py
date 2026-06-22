from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_session_flag import (  # type: ignore[import-untyped]
    VoiceAssistantSessionFlagCharacteristic,
    VoiceAssistantSessionFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantSessionFlagCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantSessionFlagCharacteristic:
        return VoiceAssistantSessionFlagCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C36"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01]), VoiceAssistantSessionFlags.SESSION_ACTIVE, "active flag"),
            CharacteristicTestData(
                bytearray([0x05]),
                VoiceAssistantSessionFlags.SESSION_ACTIVE | VoiceAssistantSessionFlags.PRIVACY_MODE_ENABLED,
                "two flags",
            ),
        ]

    def test_empty_payload_fails(self, characteristic: VoiceAssistantSessionFlagCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_build_value_too_large_fails(self, characteristic: VoiceAssistantSessionFlagCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(VoiceAssistantSessionFlags(0x1_0000))
