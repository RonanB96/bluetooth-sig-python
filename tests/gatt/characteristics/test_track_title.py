"""Tests for TrackTitleCharacteristic (2B97)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.track_title import TrackTitleCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrackTitle(CommonCharacteristicTests):
    """Test suite for TrackTitleCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> TrackTitleCharacteristic:
        return TrackTitleCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B97"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Bohemian Rhapsody"), "Bohemian Rhapsody", "Track title"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]

    def test_roundtrip(self, characteristic: TrackTitleCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Bohemian Rhapsody"), "Bohemian Rhapsody", "Track title"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
