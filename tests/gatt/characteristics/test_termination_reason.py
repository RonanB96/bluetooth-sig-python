"""Tests for TerminationReasonCharacteristic (2BC0)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.termination_reason import (
    TerminationReason,
    TerminationReasonCharacteristic,
    TerminationReasonData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTerminationReason(CommonCharacteristicTests):
    """Test suite for TerminationReasonCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> TerminationReasonCharacteristic:
        return TerminationReasonCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BC0"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=TerminationReasonData(call_index=1, reason=TerminationReason.REMOTE_PARTY_ENDED),
                description="Call 1, remote party ended",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x04]),
                expected_value=TerminationReasonData(call_index=3, reason=TerminationReason.CLIENT_ENDED),
                description="Call 3, client ended",
            ),
        ]

    def test_all_reason_codes(self, characteristic: TerminationReasonCharacteristic) -> None:
        """Test all defined termination reason codes."""
        for reason in TerminationReason:
            data = bytearray([0x00, int(reason)])
            result = characteristic.parse_value(data)
            assert result.call_index == 0
            assert result.reason == reason

    def test_roundtrip(self, characteristic: TerminationReasonCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = TerminationReasonData(call_index=2, reason=TerminationReason.LINE_BUSY)
        encoded = characteristic.build_value(original)
        result = characteristic.parse_value(encoded)
        assert result == original
