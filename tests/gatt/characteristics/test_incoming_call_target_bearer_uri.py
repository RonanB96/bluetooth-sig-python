"""Tests for Incoming Call Target Bearer URI characteristic (0x2BC2)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.incoming_call_target_bearer_uri import (
    IncomingCallTargetBearerURICharacteristic,
    IncomingCallTargetBearerURIData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIncomingCallTargetBearerURICharacteristic(CommonCharacteristicTests):
    """Test suite for Incoming Call Target Bearer URI characteristic."""

    @pytest.fixture
    def characteristic(self) -> IncomingCallTargetBearerURICharacteristic:
        return IncomingCallTargetBearerURICharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BBC"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=IncomingCallTargetBearerURIData(call_index=1, uri=""),
                description="Call index 1 with no URI",
            ),
            CharacteristicTestData(
                # call_index=4, uri="sip:x"
                input_data=bytearray([0x04, 0x73, 0x69, 0x70, 0x3A, 0x78]),
                expected_value=IncomingCallTargetBearerURIData(call_index=4, uri="sip:x"),
                description="Call index 4 with SIP URI",
            ),
        ]
