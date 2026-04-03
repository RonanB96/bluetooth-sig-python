"""Tests for SeekingSpeedCharacteristic (2B9B)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.seeking_speed import SeekingSpeedCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSeekingSpeed(CommonCharacteristicTests):
    """Test suite for SeekingSpeedCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SeekingSpeedCharacteristic:
        return SeekingSpeedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B9B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), 0, "Not seeking"),
            CharacteristicTestData(bytearray([0x01]), 1, "Seek forward"),
            CharacteristicTestData(bytearray([0xFF]), -1, "Seek backward"),
        ]
