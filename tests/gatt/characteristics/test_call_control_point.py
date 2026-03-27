"""Tests for Call Control Point characteristic (0x2BBE)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.call_control_point import (
    CallControlPointCharacteristic,
    CallControlPointData,
    CallControlPointOpCode,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestCallControlPointCharacteristic(CommonCharacteristicTests):
    """Test suite for Call Control Point characteristic."""

    @pytest.fixture
    def characteristic(self) -> CallControlPointCharacteristic:
        return CallControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BBE"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x01]),
                expected_value=CallControlPointData(
                    op_code=CallControlPointOpCode.ACCEPT,
                    call_index=1,
                ),
                description="Accept call index 1",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x03]),
                expected_value=CallControlPointData(
                    op_code=CallControlPointOpCode.TERMINATE,
                    call_index=3,
                ),
                description="Terminate call index 3",
            ),
            CharacteristicTestData(
                # Originate with URI "tel:5"
                input_data=bytearray([0x04, 0x74, 0x65, 0x6C, 0x3A, 0x35]),
                expected_value=CallControlPointData(
                    op_code=CallControlPointOpCode.ORIGINATE,
                    uri="tel:5",
                ),
                description="Originate call to tel:5",
            ),
        ]

    def test_join_opcode(self) -> None:
        """Test Join opcode with multiple call indexes."""
        char = CallControlPointCharacteristic()
        data = bytearray([0x05, 0x01, 0x02, 0x03])
        result = char.parse_value(data)
        assert result.op_code == CallControlPointOpCode.JOIN
        assert result.call_indexes == (1, 2, 3)

    def test_encode_round_trip_accept(self) -> None:
        """Verify encode/decode round-trip for accept."""
        char = CallControlPointCharacteristic()
        original = CallControlPointData(
            op_code=CallControlPointOpCode.ACCEPT,
            call_index=2,
        )
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
