"""Tests for Call State characteristic (0x2BBC)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_list_current_calls import CallFlags, CallState
from bluetooth_sig.gatt.characteristics.call_state import (
    CallStateCharacteristic,
    CallStateData,
    CallStateEntry,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCallStateCharacteristic(CommonCharacteristicTests):
    """Test suite for Call State characteristic."""

    @pytest.fixture
    def characteristic(self) -> CallStateCharacteristic:
        return CallStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BBD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(),
                expected_value=CallStateData(entries=()),
                description="No active calls",
            ),
            CharacteristicTestData(
                # call_index=1, state=ACTIVE(3), flags=OUTGOING(1)
                # bit 0=1 means outgoing per TBS v1.0 spec Table 3.7
                input_data=bytearray([0x01, 0x03, 0x01]),
                expected_value=CallStateData(
                    entries=(
                        CallStateEntry(
                            call_index=1,
                            state=CallState.ACTIVE,
                            call_flags=CallFlags.OUTGOING,
                        ),
                    ),
                ),
                description="Single active outgoing call",
            ),
            CharacteristicTestData(
                # Two entries
                input_data=bytearray(
                    [
                        0x01,
                        0x00,
                        0x00,
                        0x02,
                        0x04,
                        0x01,
                    ]
                ),
                expected_value=CallStateData(
                    entries=(
                        CallStateEntry(
                            call_index=1,
                            state=CallState.INCOMING,
                            call_flags=CallFlags(0),
                        ),
                        CallStateEntry(
                            call_index=2,
                            state=CallState.LOCALLY_HELD,
                            call_flags=CallFlags.OUTGOING,
                        ),
                    ),
                ),
                description="Two calls: incoming + locally held",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = CallStateCharacteristic()
        original = CallStateData(
            entries=(
                CallStateEntry(
                    call_index=3,
                    state=CallState.DIALING,
                    call_flags=CallFlags.WITHHELD,
                ),
            ),
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
