"""Tests for AudioInputStatusCharacteristic (2B7A)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.audio_input_status import AudioInputStatus, AudioInputStatusCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAudioInputStatus(CommonCharacteristicTests):
    """Test suite for AudioInputStatusCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> AudioInputStatusCharacteristic:
        return AudioInputStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B7A"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), AudioInputStatus.INACTIVE, "Inactive"),
            CharacteristicTestData(bytearray([0x01]), AudioInputStatus.ACTIVE, "Active"),
        ]
