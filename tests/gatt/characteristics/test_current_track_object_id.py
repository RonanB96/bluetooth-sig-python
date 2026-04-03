"""Tests for Current Track Object ID characteristic (0x2B9D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.current_track_object_id import (
    CurrentTrackObjectIdCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCurrentTrackObjectIdCharacteristic(CommonCharacteristicTests):
    """Test suite for Current Track Object ID characteristic."""

    @pytest.fixture
    def characteristic(self) -> CurrentTrackObjectIdCharacteristic:
        return CurrentTrackObjectIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B9D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=0,
                description="Zero object ID",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=10,
                description="Object ID = 10",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=281474976710655,
                description="Maximum uint48",
            ),
        ]
