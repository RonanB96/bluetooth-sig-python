"""Tests for ACSDataOutIndicateCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_data_out_indicate import (
    ACSDataOutIndicateCharacteristic,
)
from bluetooth_sig.types.acs import ACSDataPacket, ACSSegmentationHeader
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSDataOutIndicateCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSDataOutIndicateCharacteristic:
        return ACSDataOutIndicateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B32"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03, 0x42]),
                expected_value=ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=True,
                        rolling_segment_counter=0,
                    ),
                    payload=b"\x42",
                ),
                description="Single-segment indicate payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x14, 0x01, 0x02, 0x03]),
                expected_value=ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=False,
                        last_segment=False,
                        rolling_segment_counter=5,
                    ),
                    payload=b"\x01\x02\x03",
                ),
                description="Middle segment indicate payload",
            ),
        ]

    def test_encode_rejects_invalid_rolling_segment_counter(
        self, characteristic: ACSDataOutIndicateCharacteristic
    ) -> None:
        with pytest.raises(ValueError, match="rolling_segment_counter"):
            characteristic._encode_value(
                ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=False,
                        last_segment=False,
                        rolling_segment_counter=128,
                    ),
                    payload=b"\x00",
                )
            )
