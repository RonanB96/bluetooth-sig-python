"""Tests for Call Control Point Optional Opcodes characteristic (0x2BBF)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.call_control_point_optional_opcodes import (
    CallControlPointOptionalOpcodes,
    CallControlPointOptionalOpcodesCharacteristic,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCallControlPointOptionalOpcodesCharacteristic(CommonCharacteristicTests):
    """Test suite for Call Control Point Optional Opcodes characteristic."""

    @pytest.fixture
    def characteristic(self) -> CallControlPointOptionalOpcodesCharacteristic:
        return CallControlPointOptionalOpcodesCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BBF"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=CallControlPointOptionalOpcodes(0),
                description="No optional opcodes supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00]),
                expected_value=CallControlPointOptionalOpcodes.LOCAL_HOLD_AND_LOCAL_RETRIEVE,
                description="Local Hold and Retrieve supported",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x00]),
                expected_value=(
                    CallControlPointOptionalOpcodes.LOCAL_HOLD_AND_LOCAL_RETRIEVE | CallControlPointOptionalOpcodes.JOIN
                ),
                description="Both optional opcodes supported",
            ),
        ]
