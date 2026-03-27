"""Tests for BSS Control Point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.bss_control_point import (
    BSSControlPointCharacteristic,
    BSSControlPointData,
    BSSControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBSSControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for BSS Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> BSSControlPointCharacteristic:
        return BSSControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2B"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=BSSControlPointData(
                    opcode=BSSControlPointOpCode.REMOTE_SCAN_STOPPED,
                ),
                description="Remote scan stopped, no params",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0xAA, 0xBB]),
                expected_value=BSSControlPointData(
                    opcode=BSSControlPointOpCode.ADD_SOURCE,
                    parameter=b"\xaa\xbb",
                ),
                description="Add source with parameters",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05]),
                expected_value=BSSControlPointData(
                    opcode=BSSControlPointOpCode.REMOVE_SOURCE,
                ),
                description="Remove source, no params",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = BSSControlPointCharacteristic()
        original = BSSControlPointData(
            opcode=BSSControlPointOpCode.SET_BROADCAST_CODE,
            parameter=b"\x01\x02\x03",
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
