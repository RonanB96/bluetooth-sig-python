"""Tests for ProtocolModeCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.protocol_mode import (
    ProtocolMode,
    ProtocolModeCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestProtocolModeCharacteristic(CommonCharacteristicTests):
    """ProtocolModeCharacteristic test suite."""

    @pytest.fixture
    def characteristic(self) -> ProtocolModeCharacteristic:
        return ProtocolModeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A4E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=ProtocolMode.BOOT_PROTOCOL,
                description="Boot protocol mode",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=ProtocolMode.REPORT_PROTOCOL,
                description="Report protocol mode",
            ),
        ]
