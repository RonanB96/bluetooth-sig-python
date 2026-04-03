"""Tests for MediaPlayerNameCharacteristic (2B93)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.media_player_name import MediaPlayerNameCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMediaPlayerName(CommonCharacteristicTests):
    """Test suite for MediaPlayerNameCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> MediaPlayerNameCharacteristic:
        return MediaPlayerNameCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B93"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(b"Spotify"), "Spotify", "Player name"),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
