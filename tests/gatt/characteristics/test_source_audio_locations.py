"""Tests for SourceAudioLocationsCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_location import AudioLocation
from bluetooth_sig.gatt.characteristics.source_audio_locations import SourceAudioLocationsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSourceAudioLocationsCharacteristic(CommonCharacteristicTests):
    """Test suite for SourceAudioLocationsCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SourceAudioLocationsCharacteristic:
        return SourceAudioLocationsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BCC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x00]),
                expected_value=AudioLocation.FRONT_LEFT,
                description="Front left",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00, 0x00, 0x00]),
                expected_value=AudioLocation.FRONT_LEFT | AudioLocation.FRONT_RIGHT,
                description="Stereo",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00]),
                expected_value=AudioLocation(0),
                description="No location",
            ),
        ]
