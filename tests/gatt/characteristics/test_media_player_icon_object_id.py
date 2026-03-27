"""Tests for Media Player Icon Object ID characteristic (0x2B94)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.media_player_icon_object_id import (
    MediaPlayerIconObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMediaPlayerIconObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Media Player Icon Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> MediaPlayerIconObjectIdCharacteristic:
        return MediaPlayerIconObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B94"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x2A, 0x01, 0x00, 0x00, 0x00, 0x00]),
                expected_value=298,
                description="Object ID = 298 (0x012A little-endian)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = MediaPlayerIconObjectIdCharacteristic()
        original = 987654321
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
