"""Tests for Incoming Call characteristic (0x2BC1)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.incoming_call import (
    IncomingCallCharacteristic,
    IncomingCallData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIncomingCallCharacteristic(CommonCharacteristicTests):
    """Test suite for Incoming Call characteristic."""

    @pytest.fixture
    def characteristic(self) -> IncomingCallCharacteristic:
        return IncomingCallCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC1"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=IncomingCallData(call_index=1, uri=""),
                description="Call index 1 with no URI",
            ),
            CharacteristicTestData(
                # call_index=2, uri="tel:5"
                input_data=bytearray([0x02, 0x74, 0x65, 0x6C, 0x3A, 0x35]),
                expected_value=IncomingCallData(call_index=2, uri="tel:5"),
                description="Call index 2 with URI",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = IncomingCallCharacteristic()
        original = IncomingCallData(call_index=3, uri="tel:+44")
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
