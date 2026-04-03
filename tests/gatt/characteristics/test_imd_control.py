"""Tests for IMD Control characteristic (0x2C12)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.imd_control import (
    IMDControlCharacteristic,
    IMDControlData,
    IMDControlOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestIMDControlCharacteristic(CommonCharacteristicTests):
    """Test suite for IMD Control characteristic."""

    @pytest.fixture
    def characteristic(self) -> IMDControlCharacteristic:
        return IMDControlCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C12"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=IMDControlData(opcode=IMDControlOpCode.RESET_DEVICE, parameters=b""),
                description="Reset device with no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x0A, 0x0B]),
                expected_value=IMDControlData(
                    opcode=IMDControlOpCode.SET_CONFIGURATION,
                    parameters=b"\x0a\x0b",
                ),
                description="Set configuration with parameters",
            ),
        ]
