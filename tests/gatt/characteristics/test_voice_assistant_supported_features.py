from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.voice_assistant_supported_features import (  # type: ignore[import-untyped]
    VoiceAssistantSupportedFeatures,
    VoiceAssistantSupportedFeaturesCharacteristic,
)
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestVoiceAssistantSupportedFeaturesCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> VoiceAssistantSupportedFeaturesCharacteristic:
        return VoiceAssistantSupportedFeaturesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C38"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x03]),
                VoiceAssistantSupportedFeatures.TEXT_QUERY | VoiceAssistantSupportedFeatures.VOICE_QUERY,
                "2 bits",
            ),
            CharacteristicTestData(
                bytearray([0x11]),
                VoiceAssistantSupportedFeatures.TEXT_QUERY | VoiceAssistantSupportedFeatures.CONTEXT_AWARE_RESPONSES,
                "32-bit form",
            ),
        ]

    def test_empty_payload_fails(self, characteristic: VoiceAssistantSupportedFeaturesCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_build_value_too_large_fails(self, characteristic: VoiceAssistantSupportedFeaturesCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(VoiceAssistantSupportedFeatures(0x1_0000_0000))
