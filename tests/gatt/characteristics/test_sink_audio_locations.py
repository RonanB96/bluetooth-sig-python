"""Tests for SinkAudioLocationsCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_location import AudioLocation
from bluetooth_sig.gatt.characteristics.sink_audio_locations import SinkAudioLocationsCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSinkAudioLocationsCharacteristic(CommonCharacteristicTests):
    """Test suite for SinkAudioLocationsCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SinkAudioLocationsCharacteristic:
        return SinkAudioLocationsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BCA"

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
