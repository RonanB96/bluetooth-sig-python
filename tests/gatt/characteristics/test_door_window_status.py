"""Tests for DoorWindowStatus characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import DoorWindowStatusCharacteristic
from bluetooth_sig.gatt.characteristics.door_window_status import DoorWindowOpenStatus
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestDoorWindowStatusCharacteristic(CommonCharacteristicTests):
    """Test suite for DoorWindowStatus characteristic."""

    @pytest.fixture
    def characteristic(self) -> DoorWindowStatusCharacteristic:
        """Provide DoorWindowStatus characteristic."""
        return DoorWindowStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for DoorWindowStatus."""
        return "2C20"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for DoorWindowStatus."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=DoorWindowOpenStatus.OPEN,
                description="open",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=DoorWindowOpenStatus.CLOSED,
                description="closed",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=DoorWindowOpenStatus.TILTED_AJAR,
                description="tilted/ajar",
            ),
        ]
