"""Tests for BSS Response characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BSSResponseCharacteristic
from bluetooth_sig.gatt.characteristics.bss_response import BSSResponseData
from bluetooth_sig.types.bss import SplitHeader
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestBSSResponseCharacteristic(CommonCharacteristicTests):
    """Test suite for BSS Response characteristic."""

    @pytest.fixture
    def characteristic(self) -> BSSResponseCharacteristic:
        return BSSResponseCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x81]),
                expected_value=BSSResponseData(
                    split_header=SplitHeader(execute_flag=True, sequence_number=0, source_flag=True),
                    payload=b"",
                ),
                description="Server response, execute flag, no payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x81, 0x01, 0x00, 0x02]),
                expected_value=BSSResponseData(
                    split_header=SplitHeader(execute_flag=True, sequence_number=0, source_flag=True),
                    payload=b"\x01\x00\x02",
                ),
                description="Server response with 3-byte payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x04]),
                expected_value=BSSResponseData(
                    split_header=SplitHeader(execute_flag=False, sequence_number=2, source_flag=False),
                    payload=b"",
                ),
                description="Split packet, sequence 2, client direction",
            ),
        ]
