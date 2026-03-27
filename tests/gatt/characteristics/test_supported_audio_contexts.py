"""Tests for SupportedAudioContextsCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.supported_audio_contexts import (
    SupportedAudioContextsCharacteristic,
    SupportedAudioContextsData,
)
from bluetooth_sig.types.audio_context_type import AudioContextType
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestSupportedAudioContextsCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> SupportedAudioContextsCharacteristic:
        return SupportedAudioContextsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BCE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x00, 0x02, 0x00]),
                expected_value=SupportedAudioContextsData(
                    sink_audio_contexts=AudioContextType.MEDIA,
                    source_audio_contexts=AudioContextType.CONVERSATIONAL,
                ),
                description="sink=MEDIA, source=CONVERSATIONAL",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x09, 0x00, 0x40, 0x00]),
                expected_value=SupportedAudioContextsData(
                    sink_audio_contexts=AudioContextType.UNSPECIFIED | AudioContextType.GAME,
                    source_audio_contexts=AudioContextType.LIVE,
                ),
                description="sink=UNSPECIFIED|GAME, source=LIVE",
            ),
        ]
