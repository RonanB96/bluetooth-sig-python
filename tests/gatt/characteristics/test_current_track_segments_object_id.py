"""Tests for Current Track Segments Object ID characteristic (0x2B9C)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.current_track_segments_object_id import (
    CurrentTrackSegmentsObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCurrentTrackSegmentsObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Current Track Segments Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> CurrentTrackSegmentsObjectIdCharacteristic:
        return CurrentTrackSegmentsObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B9C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=5,
                description="Object ID = 5",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]
