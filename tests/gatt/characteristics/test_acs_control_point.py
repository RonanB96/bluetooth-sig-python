"""Tests for ACSControlPointCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_control_point import (
    ACSControlPointCharacteristic,
)
from bluetooth_sig.types.acs import ACSControlPointData, ACSSegmentationHeader
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSControlPointCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSControlPointCharacteristic:
        return ACSControlPointCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B33"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x01]),
                expected_value=ACSControlPointData(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=True,
                        rolling_segment_counter=0,
                    ),
                    opcode=0x01,
                    operand=b"",
                ),
                description="Single-segment opcode",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x05, 0x11, 0x05, 0x0A]),
                expected_value=ACSControlPointData(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=False,
                        rolling_segment_counter=1,
                    ),
                    opcode=0x11,
                    operand=b"\x05\x0a",
                ),
                description="First segment with operand",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x82, 0xDD]),
                expected_value=ACSControlPointData(
                    header=ACSSegmentationHeader(
                        first_segment=False,
                        last_segment=True,
                        rolling_segment_counter=32,
                    ),
                    opcode=0xDD,
                    operand=b"",
                ),
                description="Last segment with large counter",
            ),
        ]

    def test_encode_rejects_invalid_rolling_segment_counter(
        self, characteristic: ACSControlPointCharacteristic
    ) -> None:
        with pytest.raises(ValueError, match="rolling_segment_counter"):
            characteristic._encode_value(
                ACSControlPointData(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=False,
                        rolling_segment_counter=64,
                    ),
                    opcode=0x01,
                    operand=b"",
                )
            )
