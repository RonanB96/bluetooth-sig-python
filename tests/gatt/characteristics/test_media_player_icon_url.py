"""Tests for MediaPlayerIconURLCharacteristic (2B95)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.media_player_icon_url import MediaPlayerIconURLCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMediaPlayerIconURL(CommonCharacteristicTests):
    """Test suite for MediaPlayerIconURLCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> MediaPlayerIconURLCharacteristic:
        return MediaPlayerIconURLCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B95"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray(b"https://example.com/icon.png"), "https://example.com/icon.png", "Icon URL"
            ),
            CharacteristicTestData(bytearray(b""), "", "Empty string"),
        ]
