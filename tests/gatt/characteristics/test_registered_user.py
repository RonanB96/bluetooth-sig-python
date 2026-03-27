"""Tests for Registered User characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.registered_user import (
    RegisteredUserCharacteristic,
    RegisteredUserData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRegisteredUserCharacteristic(CommonCharacteristicTests):
    """Test suite for Registered User characteristic."""

    @pytest.fixture
    def characteristic(self) -> RegisteredUserCharacteristic:
        return RegisteredUserCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B37"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01]),
                expected_value=RegisteredUserData(
                    segment_index=0,
                    user_index=1,
                ),
                description="First segment, user index 1, no body",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x05, 0x41, 0x6C, 0x69, 0x63, 0x65]),
                expected_value=RegisteredUserData(
                    segment_index=2,
                    user_index=5,
                    body=b"Alice",
                ),
                description="Segment 2, user index 5, body='Alice'",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = RegisteredUserCharacteristic()
        original = RegisteredUserData(
            segment_index=1,
            user_index=3,
            body=b"\x01\x02\x03",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
