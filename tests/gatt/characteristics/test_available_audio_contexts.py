"""Tests for AvailableAudioContextsCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.available_audio_contexts import (
    AvailableAudioContextsCharacteristic,
    AvailableAudioContextsData,
)
from bluetooth_sig.types.audio_context_type import AudioContextType
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAvailableAudioContextsCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> AvailableAudioContextsCharacteristic:
        return AvailableAudioContextsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BCD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00, 0x05, 0x00]),
                expected_value=AvailableAudioContextsData(
                    sink_audio_contexts=AudioContextType.UNSPECIFIED | AudioContextType.CONVERSATIONAL,
                    source_audio_contexts=AudioContextType.UNSPECIFIED | AudioContextType.MEDIA,
                ),
                description="Sink: unspecified+conversational, source: unspecified+media",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=AvailableAudioContextsData(
                    sink_audio_contexts=AudioContextType(0),
                    source_audio_contexts=AudioContextType(0),
                ),
                description="No audio contexts available",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0x0F, 0xFF, 0x0F]),
                expected_value=AvailableAudioContextsData(
                    sink_audio_contexts=AudioContextType(0x0FFF),
                    source_audio_contexts=AudioContextType(0x0FFF),
                ),
                description="All audio contexts available for both sink and source",
            ),
        ]
