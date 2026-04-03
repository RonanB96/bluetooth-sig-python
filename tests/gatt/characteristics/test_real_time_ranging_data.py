"""Tests for Real-time Ranging Data characteristic (0x2C15)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.real_time_ranging_data import RealTimeRangingDataCharacteristic
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRealTimeRangingDataCharacteristic(CommonCharacteristicTests):
    """Test suite for Real-time Ranging Data characteristic."""

    @pytest.fixture
    def characteristic(self) -> RealTimeRangingDataCharacteristic:
        return RealTimeRangingDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C15"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte ranging data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x20, 0x30, 0x40, 0x50]),
                expected_value=b"\x10\x20\x30\x40\x50",
                description="Multi-byte ranging data",
            ),
        ]
