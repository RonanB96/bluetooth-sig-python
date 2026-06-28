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
            CharacteristicTestData(
                bytearray([VoiceAssistantSessionFlags.LISTENING_NOW]),
                VoiceAssistantSessionFlags.LISTENING_NOW,
                "listening",
            ),
            CharacteristicTestData(
                bytearray([VoiceAssistantSessionFlags.LISTENING_NOW | VoiceAssistantSessionFlags.PLAYBACK_NOW]),
                VoiceAssistantSessionFlags.LISTENING_NOW | VoiceAssistantSessionFlags.PLAYBACK_NOW,
                "two flags",
            ),
        ]

    def test_empty_payload_fails(self, characteristic: VoiceAssistantSessionFlagCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_rfu_bits_fail(self, characteristic: VoiceAssistantSessionFlagCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(VoiceAssistantSessionFlags(0x08))

    def test_two_octet_payload_fails(self, characteristic: VoiceAssistantSessionFlagCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x01, 0x00]))
