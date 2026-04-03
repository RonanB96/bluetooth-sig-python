"""Tests for Live Health Observations characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.live_health_observations import (
    LiveHealthObservationsCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestLiveHealthObservationsCharacteristic(CommonCharacteristicTests):
    """Test suite for Live Health Observations characteristic."""

    @pytest.fixture
    def characteristic(self) -> LiveHealthObservationsCharacteristic:
        return LiveHealthObservationsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B8B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=b"\x01",
                description="Single byte observation",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xAA, 0xBB, 0xCC, 0xDD]),
                expected_value=b"\xaa\xbb\xcc\xdd",
                description="Multi-byte ACOM observation data",
            ),
        ]
