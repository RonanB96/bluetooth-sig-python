"""Tests for ACSDataInCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.acs_data_in import ACSDataInCharacteristic
from bluetooth_sig.types.acs import ACSDataPacket, ACSSegmentationHeader
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestACSDataInCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> ACSDataInCharacteristic:
        return ACSDataInCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B30"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=True,
                        rolling_segment_counter=0,
                    ),
                    payload=b"",
                ),
                description="Single segment with empty payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x09, 0xDE, 0xAD, 0xBE, 0xEF]),
                expected_value=ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=True,
                        last_segment=False,
                        rolling_segment_counter=2,
                    ),
                    payload=b"\xde\xad\xbe\xef",
                ),
                description="Segmented payload",
            ),
        ]

    def test_encode_rejects_invalid_rolling_segment_counter(self, characteristic: ACSDataInCharacteristic) -> None:
        with pytest.raises(ValueError, match="rolling_segment_counter"):
            characteristic._encode_value(
                ACSDataPacket(
                    header=ACSSegmentationHeader(
                        first_segment=False,
                        last_segment=True,
                        rolling_segment_counter=99,
                    ),
                    payload=b"\x01",
                )
            )
