"""Tests for SourcePACCharacteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.source_pac import SourcePACCharacteristic, SourcePACData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestSourcePACCharacteristic(CommonCharacteristicTests):
    """Test suite for SourcePACCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> SourcePACCharacteristic:
        return SourcePACCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2BCB"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x06, 0x00, 0x00, 0x00, 0x00]),
                expected_value=SourcePACData(
                    number_of_pac_records=1,
                    raw_data=b"\x06\x00\x00\x00\x00",
                ),
                description="Single PAC record with codec data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0xAA, 0xBB]),
                expected_value=SourcePACData(
                    number_of_pac_records=2,
                    raw_data=b"\xaa\xbb",
                ),
                description="Two PAC records with raw data",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=SourcePACData(
                    number_of_pac_records=0,
                    raw_data=b"",
                ),
                description="Zero PAC records",
            ),
        ]
