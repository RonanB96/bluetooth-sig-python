"""Tests for BSS Control Point characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import BSSControlPointCharacteristic
from bluetooth_sig.gatt.characteristics.bss_control_point import BSSControlPointData
from bluetooth_sig.types.bss import SplitHeader
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


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
                input_data=bytearray([0x01]),
                expected_value=BSSControlPointData(
                    split_header=SplitHeader(execute_flag=True, sequence_number=0, source_flag=False),
                    payload=b"",
                ),
                description="Execute flag set, no payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x81, 0xAA, 0xBB]),
                expected_value=BSSControlPointData(
                    split_header=SplitHeader(execute_flag=True, sequence_number=0, source_flag=True),
                    payload=b"\xaa\xbb",
                ),
                description="Execute + source flags, 2-byte payload",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x06]),
                expected_value=BSSControlPointData(
                    split_header=SplitHeader(execute_flag=False, sequence_number=3, source_flag=False),
                    payload=b"",
                ),
                description="Split packet with sequence number 3",
            ),
        ]

    def test_split_header_sequence_number_range(self, characteristic: BSSControlPointCharacteristic) -> None:
        """Test sequence numbers across valid range (0-31)."""
        for seq in (0, 15, 31):
            header_byte = SplitHeader(execute_flag=True, sequence_number=seq, source_flag=False).to_byte()
            data = bytearray([header_byte])
            result = characteristic.parse_value(data)
            assert result.split_header.sequence_number == seq

    def test_split_header_sequence_number_out_of_range(self) -> None:
        """Test out-of-range sequence number is rejected."""
        with pytest.raises(ValueError, match="sequence_number"):
            SplitHeader(execute_flag=True, sequence_number=32, source_flag=False).to_byte()
