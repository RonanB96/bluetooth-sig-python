"""Tests for Bearer List Current Calls characteristic (0x2BB9)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bearer_list_current_calls import (
    BearerListCurrentCallsCharacteristic,
    BearerListCurrentCallsData,
    CallFlags,
    CallListItem,
    CallState,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBearerListCurrentCallsCharacteristic(CommonCharacteristicTests):
    """Test suite for Bearer List Current Calls characteristic."""

    @pytest.fixture
    def characteristic(self) -> BearerListCurrentCallsCharacteristic:
        return BearerListCurrentCallsCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BB9"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray(),
                expected_value=BearerListCurrentCallsData(calls=()),
                description="Empty call list",
            ),
            CharacteristicTestData(
                # length=7, call_index=1, state=ACTIVE(3), flags=OUTGOING(1), uri="tel:1"
                # bit 0 = 1 means outgoing per TBS v1.0 spec Table 3.7
                input_data=bytearray(
                    [
                        0x08,
                        0x01,
                        0x03,
                        0x01,
                        0x74,
                        0x65,
                        0x6C,
                        0x3A,
                        0x31,
                    ]
                ),
                expected_value=BearerListCurrentCallsData(
                    calls=(
                        CallListItem(
                            call_index=1,
                            state=CallState.ACTIVE,
                            call_flags=CallFlags.OUTGOING,
                            uri="tel:1",
                        ),
                    ),
                ),
                description="Single active outgoing call",
            ),
            CharacteristicTestData(
                # Two calls: first=length 3 no uri, second=length 6 with uri "ab"
                input_data=bytearray(
                    [
                        0x03,
                        0x02,
                        0x00,
                        0x00,
                        0x05,
                        0x03,
                        0x01,
                        0x02,
                        0x61,
                        0x62,
                    ]
                ),
                expected_value=BearerListCurrentCallsData(
                    calls=(
                        CallListItem(
                            call_index=2,
                            state=CallState.INCOMING,
                            call_flags=CallFlags(0),
                            uri="",
                        ),
                        CallListItem(
                            call_index=3,
                            state=CallState.DIALING,
                            call_flags=CallFlags.WITHHELD,
                            uri="ab",
                        ),
                    ),
                ),
                description="Two calls: incoming no URI + dialing with URI",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = BearerListCurrentCallsCharacteristic()
        original = BearerListCurrentCallsData(
            calls=(
                CallListItem(
                    call_index=5,
                    state=CallState.LOCALLY_HELD,
                    call_flags=CallFlags.OUTGOING | CallFlags.WITHHELD,
                    uri="tel:+123",
                ),
            ),
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
