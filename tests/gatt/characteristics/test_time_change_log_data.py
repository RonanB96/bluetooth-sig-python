"""Tests for Time Change Log Data characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.time_change_log_data import (
    TimeChangeLogDataCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeChangeLogDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Time Change Log Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> TimeChangeLogDataCharacteristic:
        return TimeChangeLogDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B92"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte log record",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x20, 0x30, 0x40, 0x50]),
                expected_value=b"\x10\x20\x30\x40\x50",
                description="Multi-byte log records",
            ),
        ]
