"""Tests for Stored Health Observations characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.stored_health_observations import (
    StoredHealthObservationsCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestStoredHealthObservationsCharacteristic(CommonCharacteristicTests):
    """Test suite for Stored Health Observations characteristic."""

    @pytest.fixture
    def characteristic(self) -> StoredHealthObservationsCharacteristic:
        return StoredHealthObservationsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BDD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=b"\x02",
                description="Single byte stored observation",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x11, 0x22, 0x33, 0x44, 0x55]),
                expected_value=b"\x11\x22\x33\x44\x55",
                description="Multi-byte stored ACOM observation data",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = StoredHealthObservationsCharacteristic()
        original = b"\xaa\xbb\xcc\xdd"
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
