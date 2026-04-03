"""Tests for RAS Control Point characteristic (0x2C17)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ras_control_point import (
    RASControlPointCharacteristic,
    RASControlPointData,
    RASControlPointOpCode,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRASControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for RAS Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> RASControlPointCharacteristic:
        return RASControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C17"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=RASControlPointData(
                    opcode=RASControlPointOpCode.ABORT_OPERATION,
                    parameters=b"",
                ),
                description="Abort operation with no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04, 0x01, 0x02]),
                expected_value=RASControlPointData(
                    opcode=RASControlPointOpCode.SET_FILTER,
                    parameters=b"\x01\x02",
                ),
                description="Set filter with parameters",
            ),
        ]
