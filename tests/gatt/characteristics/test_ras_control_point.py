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
                input_data=bytearray([0x05]),
                expected_value=RASControlPointData(
                    opcode=RASControlPointOpCode.ABORT_OPERATION,
                    parameters=b"",
                ),
                description="Abort operation with no parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06, 0x01, 0x02]),
                expected_value=RASControlPointData(
                    opcode=RASControlPointOpCode.FILTER_RANGING_DATA,
                    parameters=b"\x01\x02",
                ),
                description="Filter ranging data with parameters",
            ),
        ]

    def test_roundtrip(self, characteristic: RASControlPointCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        original = RASControlPointData(
            opcode=RASControlPointOpCode.GET_RANGING_DATA,
            parameters=b"\xaa\xbb",
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original
