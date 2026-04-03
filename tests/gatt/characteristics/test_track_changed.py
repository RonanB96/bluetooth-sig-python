"""Tests for Track Changed characteristic (0x2B96)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.track_changed import TrackChangedCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTrackChanged(CommonCharacteristicTests):
    """Test suite for Track Changed characteristic."""

    @pytest.fixture
    def characteristic(self) -> TrackChangedCharacteristic:
        return TrackChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B96"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(bytearray(), True, "Track changed (presence)"),
            CharacteristicTestData(bytearray(b""), True, "Track changed (empty bytes)"),
        ]

    def test_notification_only(self, characteristic: TrackChangedCharacteristic) -> None:
        """Test that empty notification decodes to True."""
        assert characteristic.parse_value(bytearray()) is True

    def test_encodes_to_empty(self, characteristic: TrackChangedCharacteristic) -> None:
        """Test that encoding produces empty bytes."""
        assert characteristic.build_value(True) == bytearray()
