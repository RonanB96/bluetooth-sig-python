"""Tests for MediaStateCharacteristic (2BA3)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.media_state import MediaState, MediaStateCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMediaState(CommonCharacteristicTests):
    """Test suite for MediaStateCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> MediaStateCharacteristic:
        return MediaStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BA3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), MediaState.INACTIVE, "Inactive"),
            CharacteristicTestData(bytearray([0x01]), MediaState.PLAYING, "Playing"),
            CharacteristicTestData(bytearray([0x02]), MediaState.PAUSED, "Paused"),
            CharacteristicTestData(bytearray([0x03]), MediaState.SEEKING, "Seeking"),
        ]

    def test_roundtrip(self, characteristic: MediaStateCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        for td in self.valid_test_data_list():
            encoded = characteristic.build_value(td.expected_value)
            result = characteristic.parse_value(encoded)
            assert result == td.expected_value

    def valid_test_data_list(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray([0x00]), MediaState.INACTIVE, "Inactive"),
            CharacteristicTestData(bytearray([0x01]), MediaState.PLAYING, "Playing"),
            CharacteristicTestData(bytearray([0x02]), MediaState.PAUSED, "Paused"),
            CharacteristicTestData(bytearray([0x03]), MediaState.SEEKING, "Seeking"),
        ]
