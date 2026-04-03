"""Tests for AudioLocationCharacteristic (2B81)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_location import AudioLocation, AudioLocationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioLocation(CommonCharacteristicTests):
    """Test suite for AudioLocationCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AudioLocationCharacteristic:
        return AudioLocationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B81"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x01, 0x00, 0x00, 0x00]), AudioLocation.FRONT_LEFT, "Front left"),
            CharacteristicTestData(bytearray([0x02, 0x00, 0x00, 0x00]), AudioLocation.FRONT_RIGHT, "Front right"),
            CharacteristicTestData(
                bytearray([0x03, 0x00, 0x00, 0x00]), AudioLocation.FRONT_LEFT | AudioLocation.FRONT_RIGHT, "Stereo"
            ),
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), AudioLocation(0), "Mono"),
            CharacteristicTestData(
                bytearray([0x00, 0x00, 0x00, 0x01]), AudioLocation.FRONT_LEFT_WIDE, "Front left wide"
            ),
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x08]), AudioLocation.RIGHT_SURROUND, "Right surround"),
        ]

    def test_all_28_locations_defined(self) -> None:
        """Verify all 28 audio locations from SIG YAML are defined."""
        assert len([m for m in AudioLocation if m.value != 0]) == 28
