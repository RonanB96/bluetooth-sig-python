from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_supported_languages import (  # type: ignore[import-untyped]
    VoiceAssistantSupportedLanguagesCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantSupportedLanguagesCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantSupportedLanguagesCharacteristic:
        return VoiceAssistantSupportedLanguagesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C37"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"en-US,fr-FR"), "en-US,fr-FR", "language list"),
            CharacteristicTestData(bytearray(b"de-DE"), "de-DE", "single language"),
        ]

    def test_invalid_utf8_fails(self, characteristic: VoiceAssistantSupportedLanguagesCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0xC3, 0x28]))

    def test_build_too_long_string_fails(self, characteristic: VoiceAssistantSupportedLanguagesCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value("z" * 300)
