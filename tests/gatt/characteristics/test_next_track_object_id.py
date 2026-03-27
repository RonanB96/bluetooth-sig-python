"""Tests for Next Track Object ID characteristic (0x2B9E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.next_track_object_id import (
    NextTrackObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestNextTrackObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Next Track Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> NextTrackObjectIdCharacteristic:
        return NextTrackObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B9E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x64, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=100,
                description="Object ID = 100",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = NextTrackObjectIdCharacteristic()
        original = 42
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
