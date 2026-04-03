"""Tests for TrackPositionCharacteristic (2B99)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.track_position import TrackPositionCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrackPosition(CommonCharacteristicTests):
    """Test suite for TrackPositionCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> TrackPositionCharacteristic:
        return TrackPositionCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B99"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), 0, "Start of track"),
            CharacteristicTestData(bytearray([0xE8, 0x03, 0x00, 0x00]), 1000, "Position 1000"),
            CharacteristicTestData(bytearray([0xFF, 0xFF, 0xFF, 0xFF]), -1, "Unavailable"),
        ]
