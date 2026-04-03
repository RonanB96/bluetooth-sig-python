"""Tests for ACSDataOutNotifyCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_data_out_notify import (
    ACSDataOutNotifyCharacteristic,
)
from bluetooth_sig.types.acs import ACSDataPacket, ACSSegmentationHeader
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSDataOutNotifyCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSDataOutNotifyCharacteristic:
        return ACSDataOutNotifyCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B31"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03, 0xFF]),
                expected_value=ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=True,
                        rolling_segment_counter=0,
                    ),
                    payload=b"\xff",
                ),
                description="Single-segment notify payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x3E, 0xAA, 0xBB]),
                expected_value=ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=False,
                        last_segment=True,
                        rolling_segment_counter=15,
                    ),
                    payload=b"\xaa\xbb",
                ),
                description="Last segment notify payload",
            ),
        ]

    def test_encode_rejects_invalid_rolling_segment_counter(
        self, characteristic: ACSDataOutNotifyCharacteristic
    ) -> None:
        with pytest.raises(ValueError, match="rolling_segment_counter"):
            characteristic._encode_value(
                ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=False,
                        rolling_segment_counter=-1,
                    ),
                    payload=b"\xaa",
                )
            )
