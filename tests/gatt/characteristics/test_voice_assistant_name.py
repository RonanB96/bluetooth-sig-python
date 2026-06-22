from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_name import (  # type: ignore[import-untyped]
    VoiceAssistantNameCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantNameCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantNameCharacteristic:
        return VoiceAssistantNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C31"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Alexa"), "Alexa", "ascii"),
            CharacteristicTestData(bytearray(b"Siri"), "Siri", "utf8"),
        ]

    def test_invalid_utf8_fails(self, characteristic: VoiceAssistantNameCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0xFF]))

    def test_build_too_long_string_fails(self, characteristic: VoiceAssistantNameCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value("y" * 300)
