"""Tests for TrackDurationCharacteristic (2B98)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.track_duration import TrackDurationCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrackDuration(CommonCharacteristicTests):
    """Test suite for TrackDurationCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> TrackDurationCharacteristic:
        return TrackDurationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B98"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), 0, "Zero duration"),
            CharacteristicTestData(bytearray([0xE8, 0x03, 0x00, 0x00]), 1000, "1000 hundredths"),
            CharacteristicTestData(bytearray([0xFF, 0xFF, 0xFF, 0xFF]), -1, "Unknown duration"),
        ]

    def test_roundtrip(self, characteristic: TrackDurationCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00, 0x00, 0x00, 0x00]), 0, "Zero duration"),
            CharacteristicTestData(bytearray([0xE8, 0x03, 0x00, 0x00]), 1000, "1000 hundredths"),
            CharacteristicTestData(bytearray([0xFF, 0xFF, 0xFF, 0xFF]), -1, "Unknown duration"),
        ]
